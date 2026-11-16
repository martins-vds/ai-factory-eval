import csv
import json
import subprocess
import sys
from io import StringIO
from pathlib import Path

import pytest
import yaml
from django.core.management import call_command
from django.core.management.base import CommandError

FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
ROOT = Path(__file__).parents[2]
MAPPING = ROOT / '.migration' / 'data' / 'mapping.yaml'


def _read_csv(path):
    with path.open(newline='', encoding='utf-8') as stream:
        return list(csv.reader(stream))


def _read_dict_csv(path):
    with path.open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))


def _write_mapping(path, mapping):
    path.write_text(yaml.safe_dump(mapping, sort_keys=False), encoding='utf-8')
    return path


@pytest.mark.django_db(transaction=True)
def test_export_data_snapshot_round_trips_fixture_rows(tmp_path):
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(MAPPING),
    )
    manifest = json.loads((FIXTURE_SNAPSHOT / 'manifest.json').read_text(encoding='utf-8'))
    out = tmp_path / 'nested' / 'target'
    command_output = StringIO()

    call_command(
        'export_data_snapshot',
        mapping=str(MAPPING),
        out=str(out),
        stdout=command_output,
    )
    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(out))
    total_rows = sum(metadata['rows'] for metadata in manifest['tables'].values())
    assert command_output.getvalue().strip() == (
        f'Exported {total_rows} rows across {len(manifest["tables"])} mapped tables.'
    )

    mapping = yaml.safe_load(MAPPING.read_text(encoding='utf-8'))
    assert {path.name for path in out.glob('*.csv')} == {
        f'{spec["target"]}.csv' for spec in mapping['tables']
    }

    for spec in mapping['tables']:
        rows = _read_csv(out / f'{spec["target"]}.csv')
        assert rows[0] == list(spec['columns'])
        assert len(rows) - 1 == manifest['tables'][spec['source']]['rows']
        primary_key = spec['key'][0]
        key_index = rows[0].index(primary_key)
        assert [int(row[key_index]) for row in rows[1:]] == sorted(
            int(row[key_index]) for row in rows[1:]
        )

    cargo = _read_dict_csv(out / 'cargo.csv')
    assert cargo[0]['last_known_location_id'] == r'\N'
    assert cargo[0]['next_expected_location_id'] == r'\N'
    assert cargo[0]['calculated_at'] == '2026-11-07T10:11:12Z'
    voyage = _read_dict_csv(out / 'voyage.csv')
    assert voyage[0]['voyage_number'] == ''
    reconciliation = subprocess.run(
        [
            sys.executable,
            str(ROOT / '.migration' / 'harness' / 'tools' / 'data_reconcile.py'),
            'reconcile',
            '--snapshot',
            str(FIXTURE_SNAPSHOT),
            '--target',
            str(out),
            '--mapping',
            str(MAPPING),
            '--report',
            str(tmp_path / 'reconciliation.md'),
        ],
        capture_output=True,
        check=False,
        text=True,
    )
    assert reconciliation.returncode == 0, reconciliation.stdout + reconciliation.stderr


@pytest.mark.django_db(transaction=True)
def test_export_data_snapshot_orders_rows_by_primary_key(tmp_path):
    from cargotracker.location.infrastructure.models import LocationRecord

    LocationRecord.objects.create(id=202, unlocode='USLAX', name='Los Angeles')
    LocationRecord.objects.create(id=101, unlocode='USNYC', name='New York')
    mapping = _write_mapping(
        tmp_path / 'mapping.yaml',
        {
            'tables': [
                {
                    'target': 'location',
                    'columns': {'id': 'id', 'unlocode': 'unlocode', 'name': 'name'},
                }
            ]
        },
    )
    out = tmp_path / 'target'

    call_command('export_data_snapshot', mapping=str(mapping), out=str(out))

    assert _read_csv(out / 'location.csv') == [
        ['id', 'unlocode', 'name'],
        ['101', 'USNYC', 'New York'],
        ['202', 'USLAX', 'Los Angeles'],
    ]


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    ('mapping', 'error'),
    [
        ({'tables': {'target': 'location'}}, 'mapping has no tables'),
        ({'tables': [{'target': None}]}, 'mapping targets must be unique table names'),
        ({'tables': [{'target': 'not_a_model'}]}, 'no registered Django model'),
        (
            {'tables': [{'target': 'location', 'columns': []}]},
            'mapping has no columns',
        ),
        (
            {'tables': [{'target': 'location', 'columns': 'id'}]},
            'mapping has no columns',
        ),
        (
            {'tables': [{'target': 'location', 'columns': {'unknown': 'id'}}]},
            'no target column',
        ),
        (
            {'tables': [{'target': 'location', 'columns': {'name': 'name'}}]},
            'mapping must include its primary key',
        ),
    ],
)
def test_export_data_snapshot_rejects_invalid_mapping(tmp_path, mapping, error):
    mapping_path = _write_mapping(tmp_path / 'mapping.yaml', mapping)

    with pytest.raises(CommandError, match=error):
        call_command(
            'export_data_snapshot',
            mapping=str(mapping_path),
            out=str(tmp_path / 'target'),
        )


def test_export_data_snapshot_rejects_non_object_mapping(tmp_path):
    mapping = tmp_path / 'mapping.yaml'
    mapping.write_text("['not a mapping']", encoding='utf-8')

    with pytest.raises(CommandError, match='mapping must be an object'):
        call_command('export_data_snapshot', mapping=str(mapping), out=str(tmp_path / 'target'))


def test_export_data_snapshot_rejects_unreadable_mapping(tmp_path):
    mapping = tmp_path / 'mapping.yaml'
    mapping.write_text('tables: [', encoding='utf-8')

    with pytest.raises(CommandError, match='unable to read mapping'):
        call_command('export_data_snapshot', mapping=str(mapping), out=str(tmp_path / 'target'))


def test_export_data_snapshot_rejects_unwritable_output(tmp_path):
    mapping = _write_mapping(
        tmp_path / 'mapping.yaml',
        {'tables': [{'target': 'location', 'columns': {'id': 'id'}}]},
    )
    output = tmp_path / 'file'
    output.write_text('not a directory', encoding='utf-8')

    with pytest.raises(CommandError, match='unable to write target export'):
        call_command('export_data_snapshot', mapping=str(mapping), out=str(output))


@pytest.mark.parametrize(
    ('provided', 'missing'),
    [
        ({'out': 'target'}, '--mapping'),
        ({'mapping': 'mapping.yaml'}, '--out'),
    ],
)
def test_export_data_snapshot_requires_mapping_and_output(provided, missing):
    with pytest.raises(CommandError, match=missing):
        call_command('export_data_snapshot', **provided)
