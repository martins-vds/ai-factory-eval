import csv
import hashlib
import json
from dataclasses import replace
from itertools import pairwise
from pathlib import Path
from shutil import copytree

import pytest
from django.core.management import call_command

from cargotracker.cargo.domain.delivery import Delivery
from cargotracker.cargo.infrastructure.models import CargoRecord, LegRecord
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.domain.handling_event import HandlingEventType
from cargotracker.handling.infrastructure.models import HandlingEventRecord
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.models import LocationRecord
from cargotracker.voyage.infrastructure.models import CarrierMovementRecord, VoyageRecord

FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = Path(__file__).parents[2] / '.migration' / 'data' / 'mapping.yaml'


def _rewrite_table(snapshot, source, changes=None, additions=()):
    path = snapshot / f'{source}.csv'
    with path.open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        fieldnames = reader.fieldnames
        rows = list(reader)
    if changes:
        rows[0].update(changes)
    rows.extend(additions)

    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest['tables'][source] = {
        'rows': len(rows),
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
    }
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
    return rows


def _valid_snapshot(tmp_path):
    snapshot = tmp_path / 'snapshot'
    copytree(FIXTURE_SNAPSHOT, snapshot)
    _rewrite_table(
        snapshot,
        'LOCATION',
        additions=[{'ID': '103', 'UNLOCODE': 'SGSIN', 'NAME': 'Singapore'}],
    )
    cargos = _rewrite_table(
        snapshot,
        'CARGO',
        {
            'SPEC_DESTINATION_ID': '103',
            'SPEC_ARRIVAL_DEADLINE': '2026-11-15',
            'TRANSPORT_STATUS': 'ONBOARD_CARRIER',
            'LAST_KNOWN_LOCATION_ID': '101',
            'CURRENT_VOYAGE_ID': '900',
            'MISDIRECTED': 'false',
            'ETA': '2026-11-10',
            'NEXT_EXPECTED_HANDLING_EVENT_TYPE': 'UNLOAD',
            'NEXT_EXPECTED_LOCATION_ID': '102',
            'NEXT_EXPECTED_VOYAGE_ID': '900',
            'UNLOADED_AT_DEST': 'false',
            'ROUTING_STATUS': 'ROUTED',
            'LAST_EVENT_ID': '72',
        },
    )
    second_cargo = cargos[0].copy()
    second_cargo.update(
        {
            'ID': '14',
            'TRACKING_ID': 'FIDELITY-0002',
            'LAST_KNOWN_LOCATION_ID': r'\N',
            'CURRENT_VOYAGE_ID': r'\N',
            'TRANSPORT_STATUS': 'NOT_RECEIVED',
            'MISDIRECTED': 'false',
            'ETA': r'\N',
            'NEXT_EXPECTED_HANDLING_EVENT_TYPE': r'\N',
            'NEXT_EXPECTED_LOCATION_ID': r'\N',
            'NEXT_EXPECTED_VOYAGE_ID': r'\N',
            'UNLOADED_AT_DEST': 'false',
            'ROUTING_STATUS': 'NOT_ROUTED',
            'LAST_EVENT_ID': r'\N',
        }
    )
    _rewrite_table(snapshot, 'CARGO', additions=[second_cargo])
    _rewrite_table(
        snapshot,
        'HANDLINGEVENT',
        {
            'TYPE': 'RECEIVE',
            'VOYAGE_ID': r'\N',
            'LOCATION_ID': '101',
        },
        additions=[
            {
                'ID': '72',
                'TYPE': 'LOAD',
                'VOYAGE_ID': '900',
                'LOCATION_ID': '101',
                'COMPLETIONTIME': '2026-11-08T12:00:00Z',
                'REGISTRATION': '2026-11-08T12:01:00Z',
                'CARGO_ID': '13',
            }
        ],
    )
    _rewrite_table(
        snapshot,
        'LEG',
        {
            'LOAD_TIME': '2026-11-08T12:00:00Z',
            'UNLOAD_TIME': '2026-11-09T10:00:00Z',
        },
        additions=[
            {
                'ID': '82',
                'LOAD_TIME': '2026-11-09T12:00:00Z',
                'UNLOAD_TIME': '2026-11-10T10:00:00Z',
                'LOAD_LOCATION_ID': '102',
                'UNLOAD_LOCATION_ID': '103',
                'VOYAGE_ID': '900',
                'CARGO_ID': '13',
            }
        ],
    )
    _rewrite_table(
        snapshot,
        'CARRIER_MOVEMENT',
        {
            'DEPARTURE_TIME': '2026-11-08T12:00:00Z',
            'ARRIVAL_TIME': '2026-11-09T10:00:00Z',
        },
        additions=[
            {
                'ID': '92',
                'DEPARTURE_TIME': '2026-11-09T12:00:00Z',
                'ARRIVAL_TIME': '2026-11-10T10:00:00Z',
                'DEPARTURE_LOCATION_ID': '102',
                'ARRIVAL_LOCATION_ID': '103',
                'VOYAGE_ID': '900',
            }
        ],
    )
    return snapshot


@pytest.fixture
def loaded_snapshot(tmp_path):
    snapshot = _valid_snapshot(tmp_path)
    call_command(
        'load_data_snapshot',
        snapshot=str(snapshot),
        mapping=str(MAPPING),
    )
    return snapshot


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_state_matches_handling_history(loaded_snapshot):
    cargo_repository = DjangoCargoRepository()
    history_repository = DjangoHandlingEventRepository()
    for cargo in cargo_repository.find_all():
        history = history_repository.lookup_handling_history_of_cargo(cargo.tracking_id)
        derived = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            cargo.delivery.calculated_at,
        )

        assert cargo.delivery.last_event_id == history.most_recent_event_id
        assert (
            derived.eta.date() if derived.eta is not None else None
        ) == (cargo.delivery.eta.date() if cargo.delivery.eta is not None else None)
        assert replace(derived, eta=cargo.delivery.eta) == replace(
            cargo.delivery, last_event_id=None
        )


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(loaded_snapshot):
    connected_pairs = 0
    for cargo in CargoRecord.objects.all():
        legs = list(
            LegRecord.objects.filter(cargo=cargo).order_by('load_time', 'pk')
        )
        for previous, following in pairwise(legs):
            assert previous.unload_location_id == following.load_location_id
            assert previous.unload_time <= following.load_time
            connected_pairs += 1

    assert connected_pairs > 0


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_events_reference_existing_voyages_and_locations(loaded_snapshot):
    events = list(HandlingEventRecord.objects.all())
    assert events

    for event in events:
        assert LocationRecord.objects.filter(pk=event.location_id).exists()
        requires_voyage = HandlingEventType(event.event_type).requires_voyage
        assert (event.voyage_id is not None) is requires_voyage
        if event.voyage_id is not None:
            assert VoyageRecord.objects.filter(pk=event.voyage_id).exists()


@pytest.mark.django_db(transaction=True)
def test_loaded_voyage_carrier_movement_schedules_are_in_order(loaded_snapshot):
    ordered_pairs = 0
    for voyage in VoyageRecord.objects.all():
        movements = list(
            CarrierMovementRecord.objects.filter(voyage=voyage).order_by(
                'departure_time', 'pk'
            )
        )
        for previous, following in pairwise(movements):
            assert previous.arrival_time <= following.departure_time
            ordered_pairs += 1

    assert ordered_pairs > 0
