import csv
from dataclasses import replace
import hashlib
from itertools import pairwise
import json
from pathlib import Path
import shutil

import pytest
from django.core.management import call_command

from cargotracker.cargo.domain.delivery import Delivery
from cargotracker.cargo.infrastructure.models import CargoRecord
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.domain.repository import HandlingEventRepository
from cargotracker.handling.infrastructure.models import HandlingEventRecord
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.models import LocationRecord
from cargotracker.voyage.infrastructure.models import CarrierMovementRecord, VoyageRecord

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = ROOT / '.migration' / 'data' / 'mapping.yaml'


def _rewrite_snapshot_table(snapshot, table, updates=None, additions=()):
    path = snapshot / f'{table}.csv'
    with path.open(newline='', encoding='utf-8') as stream:
        reader = csv.DictReader(stream)
        fieldnames = reader.fieldnames
        rows = list(reader)
    if updates:
        rows[0].update(updates)
    rows.extend(additions)
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest['tables'][table].update(
        rows=len(rows),
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
    )
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')


def _snapshot_with_consistent_delivery(tmp_path):
    snapshot = tmp_path / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)
    _rewrite_snapshot_table(
        snapshot,
        'CARGO',
        updates={
            'SPEC_DESTINATION_ID': '103',
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
    _rewrite_snapshot_table(
        snapshot,
        'HANDLINGEVENT',
        updates={'VOYAGE_ID': '\\N', 'LOCATION_ID': '101'},
        additions=[
            {
                'ID': '72',
                'TYPE': 'LOAD',
                'VOYAGE_ID': '900',
                'LOCATION_ID': '101',
                'COMPLETIONTIME': '2026-11-08T09:00:00Z',
                'REGISTRATION': '2026-11-08T09:01:00Z',
                'CARGO_ID': '13',
            }
        ],
    )
    _rewrite_snapshot_table(
        snapshot,
        'LOCATION',
        additions=[{'ID': '103', 'UNLOCODE': 'BEANR', 'NAME': 'Antwerp'}],
    )
    _rewrite_snapshot_table(
        snapshot,
        'LEG',
        updates={
            'LOAD_TIME': '2026-11-08T09:00:00Z',
            'UNLOAD_TIME': '2026-11-09T11:00:00Z',
        },
        additions=[
            {
                'ID': '82',
                'LOAD_TIME': '2026-11-09T11:00:00Z',
                'UNLOAD_TIME': '2026-11-10T12:00:00Z',
                'LOAD_LOCATION_ID': '102',
                'UNLOAD_LOCATION_ID': '103',
                'VOYAGE_ID': '900',
                'CARGO_ID': '13',
            }
        ],
    )
    _rewrite_snapshot_table(
        snapshot,
        'CARRIER_MOVEMENT',
        updates={
            'ARRIVAL_TIME': '2026-11-09T11:00:00Z',
            'DEPARTURE_TIME': '2026-11-08T09:00:00Z',
        },
        additions=[
            {
                'ID': '92',
                'ARRIVAL_TIME': '2026-11-10T12:00:00Z',
                'DEPARTURE_TIME': '2026-11-09T11:00:00Z',
                'ARRIVAL_LOCATION_ID': '103',
                'DEPARTURE_LOCATION_ID': '102',
                'VOYAGE_ID': '900',
            }
        ],
    )
    return snapshot


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_matches_its_handling_history(tmp_path):
    snapshot = _snapshot_with_consistent_delivery(tmp_path)
    call_command(
        'load_data_snapshot',
        snapshot=str(snapshot),
        mapping=str(MAPPING),
    )
    cargos = DjangoCargoRepository().find_all()
    events: HandlingEventRepository = DjangoHandlingEventRepository()

    for cargo in cargos:
        history = events.lookup_handling_history_of_cargo(cargo.tracking_id)
        derived = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            calculated_at=cargo.delivery.calculated_at,
        )

        expected_eta = (
            derived.eta.replace(hour=0, minute=0, second=0, microsecond=0)
            if derived.eta is not None
            else None
        )
        assert replace(
            derived,
            eta=expected_eta,
            last_event_id=history.most_recent_event_id,
        ) == cargo.delivery


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(tmp_path):
    snapshot = _snapshot_with_consistent_delivery(tmp_path)
    call_command(
        'load_data_snapshot',
        snapshot=str(snapshot),
        mapping=str(MAPPING),
    )

    for cargo in CargoRecord.objects.all():
        legs = list(cargo.legs.order_by('load_time', 'pk'))
        assert all(
            previous.unload_location_id == following.load_location_id
            for previous, following in pairwise(legs)
        )


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_events_reference_known_voyages_and_locations(tmp_path):
    snapshot = _snapshot_with_consistent_delivery(tmp_path)
    call_command(
        'load_data_snapshot',
        snapshot=str(snapshot),
        mapping=str(MAPPING),
    )
    location_ids = set(LocationRecord.objects.values_list('pk', flat=True))
    voyage_ids = set(VoyageRecord.objects.values_list('pk', flat=True))

    for event in HandlingEventRecord.objects.all():
        assert event.location_id in location_ids
        if event.event_type in ('LOAD', 'UNLOAD'):
            assert event.voyage_id in voyage_ids
        elif event.voyage_id is not None:
            assert event.voyage_id in voyage_ids


@pytest.mark.django_db(transaction=True)
def test_loaded_voyage_schedules_are_in_order(tmp_path):
    snapshot = _snapshot_with_consistent_delivery(tmp_path)
    call_command(
        'load_data_snapshot',
        snapshot=str(snapshot),
        mapping=str(MAPPING),
    )

    for voyage in VoyageRecord.objects.all():
        movements = list(
            CarrierMovementRecord.objects.filter(voyage=voyage).order_by('pk')
        )
        assert movements
        assert all(movement.departure_time < movement.arrival_time for movement in movements)
        assert all(
            previous.arrival_time <= following.departure_time
            and previous.arrival_location_id == following.departure_location_id
            for previous, following in pairwise(movements)
        )
