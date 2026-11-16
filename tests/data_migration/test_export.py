import csv
import hashlib
import json
from pathlib import Path

import pytest
import yaml
from django.core.management import call_command

from cargotracker.location.infrastructure.models import LocationRecord

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = ROOT / '.migration' / 'data' / 'mapping.yaml'


@pytest.mark.django_db(transaction=True)
def test_export_snapshot_round_trips_mapped_fixture_rows(tmp_path):
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(MAPPING),
    )
    LocationRecord.objects.create(id=99, unlocode='TST99', name='Test location')

    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(tmp_path))

    expected = {
        'location': (
            ['id', 'unlocode', 'name'],
            [
                ['99', 'TST99', 'Test location'],
                ['101', 'USNYC', 'New York'],
                ['102', 'NLRTM', 'Rotterdam'],
            ],
        ),
        'voyage': (['id', 'voyage_number'], [['900', '']]),
        'cargo': (
            [
                'id',
                'tracking_id',
                'origin_id',
                'spec_origin_id',
                'spec_destination_id',
                'spec_arrival_deadline',
                'transport_status',
                'last_known_location_id',
                'current_voyage_id',
                'misdirected',
                'eta',
                'next_expected_handling_event_type',
                'next_expected_location_id',
                'next_expected_voyage_id',
                'unloaded_at_dest',
                'routing_status',
                'calculated_at',
                'last_event_id',
            ],
            [
                [
                    '13',
                    'FIDELITY-0001',
                    '101',
                    '101',
                    '102',
                    '2026-12-30',
                    'NOT_RECEIVED',
                    '\\N',
                    '900',
                    'true',
                    '2026-12-29',
                    'LOAD',
                    '\\N',
                    '\\N',
                    'false',
                    'ROUTED',
                    '2026-11-07T10:11:12Z',
                    '71',
                ]
            ],
        ),
        'HandlingEvent': (
            [
                'id',
                'type',
                'voyage_id',
                'location_id',
                'completionTime',
                'registration',
                'cargo_id',
            ],
            [
                [
                    '71',
                    'RECEIVE',
                    '900',
                    '102',
                    '2026-11-07T08:12:13Z',
                    '2026-11-07T10:13:14Z',
                    '13',
                ]
            ],
        ),
        'leg': (
            [
                'id',
                'load_time',
                'unload_time',
                'load_location_id',
                'unload_location_id',
                'voyage_id',
                'cargo_id',
            ],
            [['81', '2026-11-08T08:00:00Z', '2026-11-09T11:00:00Z', '101', '102', '900', '13']],
        ),
        'carrier_movement': (
            [
                'id',
                'arrival_time',
                'departure_time',
                'arrival_location_id',
                'departure_location_id',
                'voyage_id',
            ],
            [['91', '2026-11-09T10:00:00Z', '2026-11-08T12:00:00Z', '102', '101', '900']],
        ),
    }

    for table, (header, rows) in expected.items():
        with (tmp_path / f'{table}.csv').open(newline='', encoding='utf-8') as stream:
            reader = csv.reader(stream)
            assert next(reader) == header
            assert list(reader) == rows

    mapping = yaml.safe_load(MAPPING.read_text(encoding='utf-8'))
    manifest = json.loads((tmp_path / 'manifest.json').read_text(encoding='utf-8'))
    assert manifest['null'] == '\\N'
    assert set(manifest['tables']) == {table['target'] for table in mapping['tables']}
    for table, (_, rows) in expected.items():
        output = tmp_path / f'{table}.csv'
        assert manifest['tables'][table] == {
            'rows': len(rows),
            'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
        }


@pytest.mark.django_db(transaction=True)
def test_export_snapshot_preserves_null_and_empty_string(tmp_path):
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(MAPPING),
    )

    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(tmp_path))

    with (tmp_path / 'cargo.csv').open(newline='', encoding='utf-8') as stream:
        cargo = list(csv.DictReader(stream))
    with (tmp_path / 'voyage.csv').open(newline='', encoding='utf-8') as stream:
        voyage = list(csv.DictReader(stream))
    assert cargo[0]['last_known_location_id'] == '\\N'
    assert voyage[0]['voyage_number'] == ''
