from dataclasses import replace
from itertools import pairwise
from pathlib import Path

import pytest
from django.core.management import call_command

from cargotracker.cargo.domain.delivery import Delivery
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.domain.handling_event import HandlingEventType
from cargotracker.handling.infrastructure.models import HandlingEventRecord
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.models import LocationRecord
from cargotracker.voyage.infrastructure.models import CarrierMovementRecord, VoyageRecord

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = REPOSITORY_ROOT / '.migration' / 'data' / 'snapshot'
MAPPING = REPOSITORY_ROOT / '.migration' / 'data' / 'mapping.yaml'


@pytest.fixture
def loaded_snapshot():
    call_command('load_data_snapshot', snapshot=str(SNAPSHOT), mapping=str(MAPPING))


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_deliveries_match_their_handling_histories(loaded_snapshot):
    cargo_repository = DjangoCargoRepository()
    handling_repository = DjangoHandlingEventRepository()
    cargos = cargo_repository.find_all()

    assert cargos
    for cargo in cargos:
        history = handling_repository.lookup_handling_history_of_cargo(cargo.tracking_id)
        derived_delivery = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            calculated_at=cargo.delivery.calculated_at,
        )

        assert replace(derived_delivery, last_event_id=history.most_recent_event_id) == (
            cargo.delivery
        ), cargo.tracking_id.value


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(loaded_snapshot):
    cargos = DjangoCargoRepository().find_all()

    assert cargos
    for cargo in cargos:
        assert all(
            previous.unload_location == following.load_location
            for previous, following in pairwise(cargo.itinerary.legs)
        ), cargo.tracking_id.value


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_events_reference_existing_voyages_and_locations(loaded_snapshot):
    location_ids = set(LocationRecord.objects.values_list('pk', flat=True))
    voyage_ids = set(VoyageRecord.objects.values_list('pk', flat=True))
    events = list(HandlingEventRecord.objects.order_by('pk'))

    assert events
    for event in events:
        assert event.location_id in location_ids
        if event.voyage_id is not None:
            assert event.voyage_id in voyage_ids
        if HandlingEventType(event.event_type).requires_voyage:
            assert event.voyage_id is not None


@pytest.mark.django_db(transaction=True)
def test_loaded_carrier_movement_schedules_are_in_order(loaded_snapshot):
    voyages = list(VoyageRecord.objects.order_by('pk'))

    assert voyages
    for voyage in voyages:
        movements = list(
            CarrierMovementRecord.objects.filter(voyage=voyage).order_by('departure_time', 'pk')
        )
        for previous, following in pairwise(movements):
            assert previous.arrival_time <= following.departure_time, voyage.voyage_number
            assert (
                previous.arrival_location_id == following.departure_location_id
            ), voyage.voyage_number
