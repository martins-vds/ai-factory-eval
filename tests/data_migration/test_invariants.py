from dataclasses import replace
from itertools import pairwise
from pathlib import Path

import pytest
from django.core.management import call_command

from cargotracker.cargo.domain.delivery import Delivery
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.models import HandlingEventRecord
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.models import LocationRecord
from cargotracker.voyage.infrastructure.models import CarrierMovementRecord, VoyageRecord

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = REPOSITORY_ROOT / '.migration' / 'data' / 'snapshot'
MAPPING = REPOSITORY_ROOT / '.migration' / 'data' / 'mapping.yaml'

pytestmark = pytest.mark.django_db


@pytest.fixture
def loaded_snapshot():
    call_command('load_data_snapshot', snapshot=str(SNAPSHOT), mapping=str(MAPPING))


def test_loaded_cargo_delivery_states_match_their_handling_histories(loaded_snapshot):
    cargos = DjangoCargoRepository().find_all()
    assert cargos

    handling_events = DjangoHandlingEventRepository()
    for cargo in cargos:
        history = handling_events.lookup_handling_history_of_cargo(cargo.tracking_id)
        derived_delivery = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            calculated_at=cargo.delivery.calculated_at,
        )

        assert (
            replace(derived_delivery, last_event_id=history.most_recent_event_id) == cargo.delivery
        )


def test_loaded_itinerary_legs_connect(loaded_snapshot):
    cargos = DjangoCargoRepository().find_all()
    assert cargos

    for cargo in cargos:
        assert all(
            first.unload_location == second.load_location
            for first, second in pairwise(cargo.itinerary.legs)
        )


def test_loaded_handling_events_reference_existing_voyages_and_locations(loaded_snapshot):
    events = list(HandlingEventRecord.objects.all())
    assert events
    location_ids = set(LocationRecord.objects.values_list('pk', flat=True))
    voyage_ids = set(VoyageRecord.objects.values_list('pk', flat=True))

    assert all(event.location_id in location_ids for event in events)
    assert all(event.voyage_id is None or event.voyage_id in voyage_ids for event in events)


def test_loaded_carrier_movement_schedules_are_in_order(loaded_snapshot):
    movements_by_voyage = {}
    movements = CarrierMovementRecord.objects.order_by('voyage_id', 'departure_time', 'pk')
    for movement in movements:
        assert movement.departure_time <= movement.arrival_time
        movements_by_voyage.setdefault(movement.voyage_id, []).append(movement)

    assert movements_by_voyage
    for schedule in movements_by_voyage.values():
        assert all(
            first.arrival_time <= second.departure_time for first, second in pairwise(schedule)
        )
