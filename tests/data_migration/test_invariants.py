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
from cargotracker.cargo.infrastructure.models import CargoRecord, LegRecord
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.models import HandlingEventRecord
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.models import LocationRecord
from cargotracker.voyage.infrastructure.models import CarrierMovementRecord, VoyageRecord

FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = Path(__file__).parents[2] / '.migration' / 'data' / 'mapping.yaml'


def _snapshot_for_invariants(tmp_path):
    snapshot = tmp_path / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)
    _rewrite_table(
        snapshot,
        'LOCATION',
        appended=[
            {'ID': '103', 'UNLOCODE': 'USCHI', 'NAME': 'Chicago'},
        ],
    )
    _rewrite_table(
        snapshot,
        'CARGO',
        updates={
            '13': {
                'TRANSPORT_STATUS': 'ONBOARD_CARRIER',
                'LAST_KNOWN_LOCATION_ID': '101',
                'CURRENT_VOYAGE_ID': '900',
                'MISDIRECTED': 'false',
                'ETA': '2026-11-10',
                'NEXT_EXPECTED_HANDLING_EVENT_TYPE': 'UNLOAD',
                'NEXT_EXPECTED_LOCATION_ID': '103',
                'NEXT_EXPECTED_VOYAGE_ID': '900',
                'ROUTING_STATUS': 'ROUTED',
            },
        },
    )
    _rewrite_table(
        snapshot,
        'HANDLINGEVENT',
        updates={
            '71': {
                'TYPE': 'LOAD',
                'VOYAGE_ID': '900',
                'LOCATION_ID': '101',
            },
        },
    )
    _rewrite_table(
        snapshot,
        'LEG',
        updates={
            '81': {
                'LOAD_TIME': '2026-11-08T00:00:00Z',
                'UNLOAD_TIME': '2026-11-09T00:00:00Z',
                'LOAD_LOCATION_ID': '101',
                'UNLOAD_LOCATION_ID': '103',
            },
        },
        appended=[
            {
                'ID': '82',
                'LOAD_TIME': '2026-11-09T01:00:00Z',
                'UNLOAD_TIME': '2026-11-10T00:00:00Z',
                'LOAD_LOCATION_ID': '103',
                'UNLOAD_LOCATION_ID': '102',
                'VOYAGE_ID': '900',
                'CARGO_ID': '13',
            },
        ],
    )
    _rewrite_table(
        snapshot,
        'CARRIER_MOVEMENT',
        updates={
            '91': {
                'ARRIVAL_TIME': '2026-11-09T00:00:00Z',
                'DEPARTURE_TIME': '2026-11-08T00:00:00Z',
                'ARRIVAL_LOCATION_ID': '103',
                'DEPARTURE_LOCATION_ID': '101',
            },
        },
        appended=[
            {
                'ID': '92',
                'ARRIVAL_TIME': '2026-11-10T00:00:00Z',
                'DEPARTURE_TIME': '2026-11-09T01:00:00Z',
                'ARRIVAL_LOCATION_ID': '102',
                'DEPARTURE_LOCATION_ID': '103',
                'VOYAGE_ID': '900',
            },
        ],
    )
    _refresh_manifest(snapshot)
    return snapshot


def _rewrite_table(snapshot, table, updates=None, appended=()):
    path = snapshot / f'{table}.csv'
    with path.open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        fieldnames = reader.fieldnames
        rows = list(reader)
    updates = updates or {}
    for row in rows:
        row.update(updates.get(row['ID'], {}))
    rows.extend(appended)
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _refresh_manifest(snapshot):
    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for table, entry in manifest['tables'].items():
        path = snapshot / f'{table}.csv'
        with path.open(encoding='utf-8') as stream:
            entry['rows'] = sum(1 for _ in stream) - 1
        entry['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')


def _load_snapshot(snapshot):
    call_command('load_data_snapshot', snapshot=str(snapshot), mapping=str(MAPPING))


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_matches_its_handling_history(tmp_path):
    _load_snapshot(_snapshot_for_invariants(tmp_path))

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

        assert cargo.delivery == replace(
            derived_delivery,
            last_event_id=history.most_recent_event_id,
        )


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(tmp_path):
    _load_snapshot(_snapshot_for_invariants(tmp_path))

    cargos = CargoRecord.objects.all()
    assert cargos.exists()
    for cargo in cargos:
        legs = list(LegRecord.objects.filter(cargo=cargo).order_by('load_time', 'pk'))
        assert len(legs) >= 2
        assert all(
            current.unload_location_id == following.load_location_id
            for current, following in zip(legs, legs[1:])
        )


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_events_reference_existing_voyages_and_locations(tmp_path):
    _load_snapshot(_snapshot_for_invariants(tmp_path))

    voyages = set(VoyageRecord.objects.values_list('pk', flat=True))
    locations = set(LocationRecord.objects.values_list('pk', flat=True))
    events = list(HandlingEventRecord.objects.all())
    assert events
    assert all(event.voyage_id in voyages for event in events)
    assert all(event.location_id in locations for event in events)


@pytest.mark.django_db(transaction=True)
def test_loaded_voyage_carrier_movements_are_in_schedule_order(tmp_path):
    _load_snapshot(_snapshot_for_invariants(tmp_path))

    voyages = list(VoyageRecord.objects.all())
    assert voyages
    for voyage in voyages:
        movements = list(
            CarrierMovementRecord.objects.filter(voyage=voyage).order_by('departure_time', 'pk')
        )
        assert len(movements) >= 2
        assert all(movement.departure_time <= movement.arrival_time for movement in movements)
        assert all(
            current.arrival_time <= following.departure_time
            and current.arrival_location_id == following.departure_location_id
            for current, following in zip(movements, movements[1:])
        )
