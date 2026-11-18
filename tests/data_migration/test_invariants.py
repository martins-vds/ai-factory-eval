import csv
import hashlib
import json
from dataclasses import replace
from itertools import pairwise
from pathlib import Path

import pytest
from django.core.management import call_command

from cargotracker.cargo.domain.delivery import Delivery
from cargotracker.cargo.infrastructure.models import CargoRecord, LegRecord
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.models import HandlingEventRecord
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.models import LocationRecord
from cargotracker.voyage.infrastructure.models import CarrierMovementRecord, VoyageRecord

pytestmark = pytest.mark.django_db(transaction=True)

ROOT = Path(__file__).resolve().parents[2]
MAPPING = ROOT / '.migration' / 'data' / 'mapping.yaml'
SNAPSHOT_TABLES = {
    'LOCATION': (
        ['ID', 'UNLOCODE', 'NAME'],
        [
            ['1', 'USNYC', 'New York'],
            ['2', 'NLRTM', 'Rotterdam'],
            ['3', 'FIHEL', 'Helsinki'],
        ],
    ),
    'VOYAGE': (['ID', 'VOYAGE_NUMBER'], [['10', 'V001']]),
    'CARGO': (
        [
            'ID',
            'TRACKING_ID',
            'ORIGIN_ID',
            'SPEC_ORIGIN_ID',
            'SPEC_DESTINATION_ID',
            'SPEC_ARRIVAL_DEADLINE',
            'TRANSPORT_STATUS',
            'LAST_KNOWN_LOCATION_ID',
            'CURRENT_VOYAGE_ID',
            'MISDIRECTED',
            'ETA',
            'NEXT_EXPECTED_HANDLING_EVENT_TYPE',
            'NEXT_EXPECTED_LOCATION_ID',
            'NEXT_EXPECTED_VOYAGE_ID',
            'UNLOADED_AT_DEST',
            'ROUTING_STATUS',
            'CALCULATED_AT',
            'LAST_EVENT_ID',
        ],
        [
            [
                '100',
                'DM05F-001',
                '1',
                '1',
                '3',
                '2026-12-01',
                'ONBOARD_CARRIER',
                '1',
                '10',
                'false',
                '2026-11-11',
                'UNLOAD',
                '2',
                '10',
                'false',
                'ROUTED',
                '2026-11-07T12:00:00Z',
                '201',
            ]
        ],
    ),
    'HANDLINGEVENT': (
        [
            'ID',
            'TYPE',
            'VOYAGE_ID',
            'LOCATION_ID',
            'COMPLETIONTIME',
            'REGISTRATION',
            'CARGO_ID',
        ],
        [
            ['200', 'RECEIVE', None, '1', '2026-11-06T09:00:00Z', '2026-11-06T09:01:00Z', '100'],
            ['201', 'LOAD', '10', '1', '2026-11-07T11:00:00Z', '2026-11-07T11:01:00Z', '100'],
        ],
    ),
    'LEG': (
        [
            'ID',
            'LOAD_TIME',
            'UNLOAD_TIME',
            'LOAD_LOCATION_ID',
            'UNLOAD_LOCATION_ID',
            'VOYAGE_ID',
            'CARGO_ID',
        ],
        [
            ['301', '2026-11-08T10:00:00Z', '2026-11-09T10:00:00Z', '1', '2', '10', '100'],
            ['302', '2026-11-10T10:00:00Z', '2026-11-11T10:00:00Z', '2', '3', '10', '100'],
        ],
    ),
    'CARRIER_MOVEMENT': (
        [
            'ID',
            'ARRIVAL_TIME',
            'DEPARTURE_TIME',
            'ARRIVAL_LOCATION_ID',
            'DEPARTURE_LOCATION_ID',
            'VOYAGE_ID',
        ],
        [
            ['402', '2026-11-11T10:00:00Z', '2026-11-10T10:00:00Z', '3', '2', '10'],
            ['401', '2026-11-09T10:00:00Z', '2026-11-08T10:00:00Z', '2', '1', '10'],
        ],
    ),
}


def _write_snapshot(directory):
    directory.mkdir()
    tables = {}
    for table, (header, rows) in SNAPSHOT_TABLES.items():
        path = directory / f'{table}.csv'
        with path.open('w', encoding='utf-8', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(header)
            writer.writerows([['\\N' if value is None else value for value in row] for row in rows])
        tables[table] = {
            'rows': len(rows),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    (directory / 'manifest.json').write_text(
        json.dumps({'null': '\\N', 'tables': tables}),
        encoding='utf-8',
    )
    return directory


@pytest.fixture
def loaded_snapshot(tmp_path):
    snapshot = _write_snapshot(tmp_path / 'snapshot')
    call_command(
        'load_data_snapshot',
        snapshot=str(snapshot),
        mapping=str(MAPPING),
    )


def test_loaded_cargo_delivery_matches_its_handling_history(loaded_snapshot):
    cargo_repository = DjangoCargoRepository()
    history_repository = DjangoHandlingEventRepository()

    cargoes = cargo_repository.find_all()
    assert cargoes
    for cargo in cargoes:
        history = history_repository.lookup_handling_history_of_cargo(cargo.tracking_id)
        expected = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            cargo.delivery.calculated_at,
        )
        expected = replace(
            expected,
            eta=(
                expected.eta.replace(hour=0, minute=0, second=0, microsecond=0)
                if expected.eta is not None
                else None
            ),
            last_event_id=history.most_recent_event_id,
        )

        assert cargo.delivery == expected, cargo.tracking_id.value


def test_loaded_itinerary_legs_connect(loaded_snapshot):
    cargoes = DjangoCargoRepository().find_all()

    assert cargoes
    assert any(cargo.itinerary.legs for cargo in cargoes)
    for cargo in cargoes:
        for previous, following in pairwise(cargo.itinerary.legs):
            assert previous.unload_location == following.load_location


def test_loaded_handling_events_reference_existing_voyages_and_locations(loaded_snapshot):
    location_ids = set(LocationRecord.objects.values_list('pk', flat=True))
    voyage_ids = set(VoyageRecord.objects.values_list('pk', flat=True))
    events = list(HandlingEventRecord.objects.order_by('pk'))

    assert events
    for event in events:
        assert event.location_id in location_ids
        assert event.voyage_id is None or event.voyage_id in voyage_ids


def test_loaded_voyage_carrier_movements_are_in_schedule_order(loaded_snapshot):
    assert CargoRecord.objects.exists()
    assert LegRecord.objects.exists()
    for voyage in VoyageRecord.objects.order_by('pk'):
        movements = list(
            CarrierMovementRecord.objects.filter(voyage=voyage).order_by('departure_time', 'pk')
        )
        for movement in movements:
            assert movement.departure_time <= movement.arrival_time
        for previous, following in pairwise(movements):
            assert previous.arrival_time <= following.departure_time
