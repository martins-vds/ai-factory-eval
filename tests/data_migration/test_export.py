import csv
from pathlib import Path

import pytest
import yaml
from django.core.management import call_command
from test_load import MAPPING

from cargotracker.location.infrastructure.models import LocationRecord

FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'


def _write_mapping(tmp_path):
    mapping_file = tmp_path / 'mapping.yaml'
    mapping_file.write_text(yaml.safe_dump(MAPPING, sort_keys=False), encoding='utf-8')
    return mapping_file


@pytest.mark.django_db(transaction=True)
def test_export_data_snapshot_round_trips_fixture_rows_and_preserves_nulls(tmp_path):
    mapping_file = _write_mapping(tmp_path)
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(mapping_file),
    )
    export_dir = tmp_path / 'export'

    call_command('export_data_snapshot', mapping=str(mapping_file), out=str(export_dir))

    expected = {
        'location': [
            ['101', 'USNYC', 'New York'],
            ['102', 'NLRTM', 'Rotterdam'],
        ],
        'voyage': [['900', '']],
        'cargo': [
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
                'True',
                '2026-12-29',
                'LOAD',
                '\\N',
                '\\N',
                'False',
                'ROUTED',
                '2026-11-07T10:11:12+00:00',
                '71',
            ]
        ],
        'HandlingEvent': [
            [
                '71',
                'RECEIVE',
                '900',
                '102',
                '2026-11-07T08:12:13+00:00',
                '2026-11-07T10:13:14+00:00',
                '13',
            ]
        ],
        'leg': [
            [
                '81',
                '2026-11-08T08:00:00+00:00',
                '2026-11-09T11:00:00+00:00',
                '101',
                '102',
                '900',
                '13',
            ]
        ],
        'carrier_movement': [
            [
                '91',
                '2026-11-09T10:00:00+00:00',
                '2026-11-08T12:00:00+00:00',
                '102',
                '101',
                '900',
            ]
        ],
    }

    for spec in MAPPING['tables']:
        with (export_dir / f'{spec["target"]}.csv').open(newline='', encoding='utf-8') as stream:
            rows = list(csv.reader(stream))
        assert rows[0] == list(spec['columns'])
        assert rows[1:] == expected[spec['target']]

    with (export_dir / 'cargo.csv').open(newline='', encoding='utf-8') as stream:
        cargo = next(csv.DictReader(stream))
    with (export_dir / 'voyage.csv').open(newline='', encoding='utf-8') as stream:
        voyage = next(csv.DictReader(stream))

    assert cargo['last_known_location_id'] == '\\N'
    assert voyage['voyage_number'] == ''
    assert '""' in (export_dir / 'voyage.csv').read_text(encoding='utf-8')


@pytest.mark.django_db(transaction=True)
def test_export_data_snapshot_orders_rows_by_primary_key(tmp_path):
    LocationRecord.objects.create(id=20, unlocode='TST20', name='Later')
    LocationRecord.objects.create(id=10, unlocode='TST10', name='Earlier')

    export_dir = tmp_path / 'export'
    mapping_file = _write_mapping(tmp_path)
    call_command('export_data_snapshot', mapping=str(mapping_file), out=str(export_dir))

    with (export_dir / 'location.csv').open(newline='', encoding='utf-8') as stream:
        ids = [row['id'] for row in csv.DictReader(stream)]

    assert ids == ['10', '20']
