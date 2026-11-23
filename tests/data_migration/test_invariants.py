from dataclasses import replace
from itertools import pairwise
from pathlib import Path

import pytest
from django.core.management import call_command

from cargotracker.cargo.domain.delivery import Delivery
from cargotracker.cargo.infrastructure.models import CargoRecord
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.models import HandlingEventRecord
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.models import LocationRecord
from cargotracker.voyage.infrastructure.models import CarrierMovementRecord, VoyageRecord

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / '.migration' / 'data' / 'snapshot'
MAPPING = ROOT / '.migration' / 'data' / 'mapping.yaml'


@pytest.fixture
def loaded_snapshot(db):
    call_command(
        'load_data_snapshot',
        snapshot=str(SNAPSHOT),
        mapping=str(MAPPING),
    )


def test_cargo_delivery_state_matches_its_handling_history(loaded_snapshot):
    cargos = DjangoCargoRepository().find_all()
    history_repository = DjangoHandlingEventRepository()

    assert cargos
    for cargo in cargos:
        history = history_repository.lookup_handling_history_of_cargo(cargo.tracking_id)
        expected = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            cargo.delivery.calculated_at,
        )

        assert cargo.delivery == replace(expected, last_event_id=history.most_recent_event_id)


def test_each_itinerary_has_connected_legs(loaded_snapshot):
    cargos = DjangoCargoRepository().find_all()

    assert CargoRecord.objects.filter(legs__isnull=False).exists()
    for cargo in cargos:
        assert all(
            previous.unload_location == following.load_location
            for previous, following in pairwise(cargo.itinerary.legs)
        )


def test_each_handling_event_references_existing_voyage_and_location(loaded_snapshot):
    events = list(HandlingEventRecord.objects.all())
    location_ids = set(LocationRecord.objects.values_list('pk', flat=True))
    voyage_ids = set(VoyageRecord.objects.values_list('pk', flat=True))

    assert events
    for event in events:
        assert event.location_id in location_ids
        assert event.voyage_id is None or event.voyage_id in voyage_ids
        if event.event_type in {'LOAD', 'UNLOAD'}:
            assert event.voyage_id in voyage_ids


def test_each_voyage_carrier_movement_schedule_is_in_order(loaded_snapshot):
    voyage_ids = CarrierMovementRecord.objects.values_list('voyage_id', flat=True).distinct()

    assert voyage_ids.exists()
    for voyage_id in voyage_ids:
        movements = list(
            CarrierMovementRecord.objects.filter(voyage_id=voyage_id).order_by(
                'departure_time', 'pk'
            )
        )
        for movement in movements:
            assert movement.departure_time < movement.arrival_time

        for previous, following in pairwise(movements):
            assert previous.arrival_time <= following.departure_time
            assert previous.arrival_location_id == following.departure_location_id
