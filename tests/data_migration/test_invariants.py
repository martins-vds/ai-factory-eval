from dataclasses import replace
from pathlib import Path

import pytest
from django.core.management import call_command

from cargotracker.cargo.domain.delivery import Delivery
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository

FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = Path(__file__).resolve().parents[2] / '.migration' / 'data' / 'mapping.yaml'


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_state_matches_its_handling_history():
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(MAPPING),
    )

    cargo = DjangoCargoRepository().find(TrackingId('FIDELITY-0001'))
    history = DjangoHandlingEventRepository().lookup_handling_history_of_cargo(cargo.tracking_id)
    derived = Delivery.derived_from(
        cargo.route_specification,
        cargo.itinerary,
        history,
        calculated_at=cargo.delivery.calculated_at,
    )

    assert cargo.delivery == replace(derived, last_event_id=history.most_recent_event_id)
