import csv
import hashlib
import json
import shutil
from dataclasses import replace
from pathlib import Path

import pytest
from django.core.management import call_command

from cargotracker.cargo.domain.delivery import Delivery
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.models import CargoRecord
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.models import HandlingEventRecord
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.models import LocationRecord
from cargotracker.voyage.infrastructure.models import CarrierMovementRecord, VoyageRecord

FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = Path(__file__).parents[2] / '.migration' / 'data' / 'mapping.yaml'


def _read_table(snapshot, table):
    with (snapshot / f'{table}.csv').open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def _write_table(snapshot, table, updates=None, additions=()):
    path = snapshot / f'{table}.csv'
    with path.open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        headers = reader.fieldnames
        rows = list(reader)

    if updates:
        rows[0].update(updates)
    rows.extend(additions)

    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest['tables'][table].update(
        rows=len(rows),
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
    )
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')


def _load_invariant_snapshot(tmp_path):
    snapshot = tmp_path / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)

    _write_table(
        snapshot,
        'LOCATION',
        additions=[{'ID': '103', 'UNLOCODE': 'SGSIN', 'NAME': 'Singapore'}],
    )
    _write_table(
        snapshot,
        'CARGO',
        updates={
            'SPEC_DESTINATION_ID': '103',
            'TRANSPORT_STATUS': 'ONBOARD_CARRIER',
            'LAST_KNOWN_LOCATION_ID': '101',
            'CURRENT_VOYAGE_ID': '900',
            'MISDIRECTED': 'false',
            'ETA': '2026-11-11',
            'NEXT_EXPECTED_HANDLING_EVENT_TYPE': 'UNLOAD',
            'NEXT_EXPECTED_LOCATION_ID': '102',
            'NEXT_EXPECTED_VOYAGE_ID': '900',
            'UNLOADED_AT_DEST': 'false',
            'ROUTING_STATUS': 'ROUTED',
        },
    )
    _write_table(
        snapshot,
        'HANDLINGEVENT',
        updates={'TYPE': 'LOAD', 'LOCATION_ID': '101'},
    )
    _write_table(
        snapshot,
        'LEG',
        additions=[
            {
                'ID': '82',
                'LOAD_TIME': '2026-11-10T08:00:00Z',
                'UNLOAD_TIME': '2026-11-11T11:00:00Z',
                'LOAD_LOCATION_ID': '102',
                'UNLOAD_LOCATION_ID': '103',
                'VOYAGE_ID': '900',
                'CARGO_ID': '13',
            }
        ],
    )
    _write_table(
        snapshot,
        'CARRIER_MOVEMENT',
        additions=[
            {
                'ID': '92',
                'ARRIVAL_TIME': '2026-11-11T10:00:00Z',
                'DEPARTURE_TIME': '2026-11-10T08:00:00Z',
                'ARRIVAL_LOCATION_ID': '103',
                'DEPARTURE_LOCATION_ID': '102',
                'VOYAGE_ID': '900',
            }
        ],
    )

    call_command('load_data_snapshot', snapshot=str(snapshot), mapping=str(MAPPING))


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_matches_its_itinerary_and_handling_history(tmp_path):
    _load_invariant_snapshot(tmp_path)
    cargo_repository = DjangoCargoRepository()
    history_repository = DjangoHandlingEventRepository()

    for cargo in cargo_repository.find_all():
        history = history_repository.lookup_handling_history_of_cargo(cargo.tracking_id)
        expected = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            cargo.delivery.calculated_at,
        )
        stored = cargo.delivery

        assert replace(stored, eta=expected.eta, last_event_id=None) == expected
        assert stored.last_event_id == history.most_recent_event_id
        assert (stored.eta.date() if stored.eta is not None else None) == (
            expected.eta.date() if expected.eta is not None else None
        )


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(tmp_path):
    _load_invariant_snapshot(tmp_path)

    for cargo in CargoRecord.objects.all():
        legs = list(cargo.legs.order_by('load_time', 'pk'))
        assert len(legs) == 2
        assert all(
            current.load_location_id == previous.unload_location_id
            for previous, current in zip(legs, legs[1:], strict=False)
        )


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_event_references_exist(tmp_path):
    _load_invariant_snapshot(tmp_path)
    location_ids = set(LocationRecord.objects.values_list('pk', flat=True))
    voyage_ids = set(VoyageRecord.objects.values_list('pk', flat=True))
    events = list(HandlingEventRecord.objects.all())

    assert events
    assert all(event.location_id in location_ids for event in events)
    assert all(
        event.voyage_id is None or event.voyage_id in voyage_ids for event in events
    )


@pytest.mark.django_db(transaction=True)
def test_loaded_voyage_carrier_movements_are_in_schedule_order(tmp_path):
    _load_invariant_snapshot(tmp_path)

    for voyage in VoyageRecord.objects.all():
        movements = list(
            CarrierMovementRecord.objects.filter(voyage=voyage).order_by('departure_time', 'pk')
        )
        assert len(movements) == 2
        assert all(movement.departure_time < movement.arrival_time for movement in movements)
        assert all(
            previous.arrival_time <= current.departure_time
            and previous.arrival_location_id == current.departure_location_id
            for previous, current in zip(movements, movements[1:], strict=False)
        )
