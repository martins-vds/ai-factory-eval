from dataclasses import replace
from itertools import pairwise
from pathlib import Path

import pytest
from django.core.management import call_command

from cargotracker.cargo.domain.delivery import Delivery
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.models import CargoRecord
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.domain.handling_event import HandlingEventType
from cargotracker.handling.infrastructure.models import HandlingEventRecord
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.voyage.infrastructure.models import CarrierMovementRecord, VoyageRecord

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / '.migration' / 'data' / 'snapshot'
MAPPING = ROOT / '.migration' / 'data' / 'mapping.yaml'


@pytest.fixture
def loaded_snapshot(transactional_db):
    call_command('load_data_snapshot', snapshot=str(SNAPSHOT), mapping=str(MAPPING))


def test_loaded_cargo_delivery_matches_handling_history(loaded_snapshot):
    cargo_repository = DjangoCargoRepository()
    handling_repository = DjangoHandlingEventRepository()
    records = CargoRecord.objects.all()
    assert records.exists()

    for record in records:
        cargo = cargo_repository.find(TrackingId(record.tracking_id))
        history = handling_repository.lookup_handling_history_of_cargo(cargo.tracking_id)
        expected = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            calculated_at=cargo.delivery.calculated_at,
        )

        assert cargo.delivery == replace(expected, last_event_id=history.most_recent_event_id)


def test_loaded_itinerary_legs_connect(loaded_snapshot):
    cargos = DjangoCargoRepository().find_all()
    assert cargos

    for cargo in cargos:
        for previous, following in pairwise(cargo.itinerary.legs):
            assert previous.unload_location == following.load_location


def test_loaded_handling_events_reference_existing_voyages_and_locations(loaded_snapshot):
    events = HandlingEventRecord.objects.select_related('voyage', 'location').all()
    assert events.exists()

    for event in events:
        assert event.location_id is not None
        assert event.location.pk == event.location_id
        if HandlingEventType(event.event_type).requires_voyage:
            assert event.voyage_id is not None
        if event.voyage_id is not None:
            assert event.voyage.pk == event.voyage_id


def test_loaded_voyage_carrier_movements_are_in_schedule_order(loaded_snapshot):
    voyages = VoyageRecord.objects.all()
    assert voyages.exists()

    for voyage in voyages:
        movements = list(
            CarrierMovementRecord.objects.filter(voyage=voyage).order_by('departure_time', 'pk')
        )
        for movement in movements:
            assert movement.departure_time <= movement.arrival_time
        for previous, following in pairwise(movements):
            assert previous.arrival_time <= following.departure_time
            assert previous.arrival_location_id == following.departure_location_id
