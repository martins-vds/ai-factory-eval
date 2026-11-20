import csv
from io import StringIO
from pathlib import Path

import pytest
import yaml
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings

from cargotracker.location.infrastructure.models import LocationRecord

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING_PATH = ROOT / '.migration' / 'data' / 'mapping.yaml'
MAPPING = yaml.safe_load(MAPPING_PATH.read_text(encoding='utf-8'))


def _read_csv(path):
    with path.open(newline='', encoding='utf-8') as stream:
        return list(csv.reader(stream))


def _load_fixture():
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(MAPPING_PATH),
    )


@pytest.mark.django_db(transaction=True)
@override_settings(USE_TZ=False)
def test_export_snapshot_round_trips_fixture_rows(tmp_path):
    _load_fixture()
    output_dir = tmp_path / 'nested' / 'target-export'
    stdout = StringIO()

    call_command(
        'export_data_snapshot',
        mapping=str(MAPPING_PATH),
        out=str(output_dir),
        stdout=stdout,
    )
    assert stdout.getvalue().strip() == 'Exported 7 rows across 6 mapped tables.'

    assert {path.stem for path in output_dir.glob('*.csv')} == {
        spec['target'] for spec in MAPPING['tables']
    }
    exported = {}
    for spec in MAPPING['tables']:
        data = _read_csv(output_dir / f'{spec["target"]}.csv')
        source_data = _read_csv(FIXTURE_SNAPSHOT / f'{spec["source"]}.csv')
        assert data[0] == list(spec['columns'])
        assert len(data) - 1 == len(source_data) - 1
        exported[spec['target']] = data

    assert exported['location'][1:] == [
        ['101', 'USNYC', 'New York'],
        ['102', 'NLRTM', 'Rotterdam'],
    ]
    assert exported['voyage'][1:] == [['900', '']]
    assert exported['cargo'][1:] == [
        [
            '13',
            'FIDELITY-0001',
            '101',
            '101',
            '102',
            '2026-12-30',
            'NOT_RECEIVED',
            r'\N',
            '900',
            'true',
            '2026-12-29',
            'LOAD',
            r'\N',
            r'\N',
            'false',
            'ROUTED',
            '2026-11-07T10:11:12Z',
            '71',
        ]
    ]
    cargo_header, cargo_row = exported['cargo'][0], exported['cargo'][1]
    assert cargo_row[cargo_header.index('last_known_location_id')] == r'\N'
    assert cargo_row[cargo_header.index('next_expected_location_id')] == r'\N'
    assert exported['HandlingEvent'][1:] == [
        [
            '71',
            'RECEIVE',
            '900',
            '102',
            '2026-11-07T08:12:13Z',
            '2026-11-07T10:13:14Z',
            '13',
        ]
    ]
    assert exported['leg'][1:] == [
        ['81', '2026-11-08T08:00:00Z', '2026-11-09T11:00:00Z', '101', '102', '900', '13']
    ]
    assert exported['carrier_movement'][1:] == [
        ['91', '2026-11-09T10:00:00Z', '2026-11-08T12:00:00Z', '102', '101', '900']
    ]
    call_command('export_data_snapshot', mapping=str(MAPPING_PATH), out=str(output_dir))
    assert {target: _read_csv(output_dir / f'{target}.csv') for target in exported} == exported


@pytest.mark.django_db(transaction=True)
def test_export_snapshot_orders_rows_by_primary_key(tmp_path):
    _load_fixture()
    LocationRecord.objects.create(id=100, unlocode='AUSYD', name='Sydney')
    output_dir = tmp_path / 'target-export'

    call_command('export_data_snapshot', mapping=str(MAPPING_PATH), out=str(output_dir))

    assert [row[0] for row in _read_csv(output_dir / 'location.csv')[1:]] == [
        '100',
        '101',
        '102',
    ]


@pytest.mark.parametrize(
    'tables',
    [
        [],
        [MAPPING['tables'][0], MAPPING['tables'][0]],
    ],
)
def test_export_snapshot_rejects_empty_or_duplicate_table_mappings(tmp_path, tables):
    mapping = tmp_path / 'invalid-mapping.yaml'
    mapping.write_text(yaml.safe_dump({'tables': tables}), encoding='utf-8')

    with pytest.raises(CommandError):
        call_command(
            'export_data_snapshot',
            mapping=str(mapping),
            out=str(tmp_path / 'target-export'),
        )


@pytest.mark.parametrize(
    'options',
    [
        {'out': 'target-export'},
        {'mapping': str(MAPPING_PATH)},
    ],
)
def test_export_snapshot_requires_mapping_and_output(options):
    with pytest.raises(CommandError):
        call_command('export_data_snapshot', **options)
