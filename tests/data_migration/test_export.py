import csv
import json
import re
from datetime import datetime, timedelta, timezone
from io import StringIO
from pathlib import Path

import pytest
import yaml
from django.core.management import call_command
from django.core.management.base import CommandError

from cargotracker.data_migration.exporter import DataExportError, _format_value, export_snapshot
from cargotracker.data_migration.management.commands.export_data_snapshot import Command

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING_FILE = ROOT / '.migration' / 'data' / 'mapping.yaml'


@pytest.mark.django_db(transaction=True)
def test_export_data_snapshot_round_trips_fixture_rows_and_preserves_nulls(tmp_path):
    mapping = yaml.safe_load(MAPPING_FILE.read_text(encoding='utf-8'))
    handling_event = next(
        table for table in mapping['tables'] if table['target'] == 'HandlingEvent'
    )
    handling_event['columns']['completion_time'] = handling_event['columns'].pop('completionTime')
    mapping_file = tmp_path / 'mapping.yaml'
    mapping_file.write_text(yaml.safe_dump(mapping, sort_keys=False), encoding='utf-8')

    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(mapping_file),
    )
    output = tmp_path / 'nested' / 'export'
    stdout = StringIO()
    call_command(
        'export_data_snapshot',
        mapping=str(mapping_file),
        out=str(output),
        stdout=stdout,
    )
    assert stdout.getvalue() == 'Exported 6 mapped tables.\n'
    call_command(
        'export_data_snapshot',
        mapping=str(mapping_file),
        out=str(output),
    )

    manifest = json.loads((FIXTURE_SNAPSHOT / 'manifest.json').read_text(encoding='utf-8'))
    assert {path.stem for path in output.glob('*.csv')} == {
        table['target'] for table in mapping['tables']
    }

    exported = {}
    for spec in mapping['tables']:
        with (output / f'{spec["target"]}.csv').open(newline='', encoding='utf-8') as stream:
            reader = csv.DictReader(stream)
            rows = list(reader)
        assert reader.fieldnames == list(spec['columns'])
        assert len(rows) == manifest['tables'][spec['source']]['rows']
        assert [int(row[spec['key'][0]]) for row in rows] == sorted(
            int(row[spec['key'][0]]) for row in rows
        )
        exported[spec['target']] = rows

    assert exported['location'] == [
        {'id': '101', 'unlocode': 'USNYC', 'name': 'New York'},
        {'id': '102', 'unlocode': 'NLRTM', 'name': 'Rotterdam'},
    ]
    assert exported['voyage'] == [{'id': '900', 'voyage_number': ''}]
    assert exported['cargo'][0]['last_known_location_id'] == r'\N'
    assert exported['cargo'][0]['calculated_at'] == '2026-11-07T10:11:12Z'


@pytest.mark.parametrize(
    ('tables', 'message'),
    [
        (None, 'mapping has no tables'),
        ([], 'mapping has no tables'),
        ([None], 'mapping has no tables'),
        ([{'target': None, 'columns': {'id': 'ID'}}], 'mapping targets must be unique table names'),
        (
            [
                {'target': 'location', 'columns': {'id': 'ID'}},
                {'target': 'location', 'columns': {'id': 'ID'}},
            ],
            'mapping targets must be unique table names',
        ),
        (
            [{'target': '../location', 'columns': {'id': 'ID'}}],
            '../location: invalid target table name',
        ),
        (
            [{'target': 'missing', 'columns': {'id': 'ID'}}],
            'missing: no registered Django model for target table',
        ),
        ([{'target': 'location', 'columns': None}], 'location: mapping has no columns'),
        ([{'target': 'location', 'columns': []}], 'location: mapping has no columns'),
        ([{'target': 'location', 'columns': ['id']}], 'location: mapping has no columns'),
        (
            [{'target': 'location', 'columns': {'missing': 'NOPE'}}],
            "location: no target column 'missing'",
        ),
        (
            [{'target': 'location', 'columns': {'name': 'NAME'}}],
            'location: mapping must include its primary key',
        ),
    ],
)
def test_export_rejects_invalid_mapping(tmp_path, tables, message):
    mapping = yaml.safe_load(MAPPING_FILE.read_text(encoding='utf-8'))
    mapping['tables'] = tables
    mapping_file = tmp_path / 'mapping.yaml'
    mapping_file.write_text(yaml.safe_dump(mapping), encoding='utf-8')

    with pytest.raises(DataExportError, match=re.escape(message)):
        export_snapshot(mapping_file, tmp_path / 'export')


def test_export_rejects_unreadable_and_non_object_mapping(tmp_path):
    missing = tmp_path / 'missing.yaml'
    with pytest.raises(DataExportError) as error:
        export_snapshot(missing, tmp_path / 'export')
    assert str(error.value).startswith(f'{missing}: unable to read mapping:')
    assert not str(error.value).endswith('XX')

    mapping_file = tmp_path / 'mapping.yaml'
    mapping_file.write_text('- invalid', encoding='utf-8')
    with pytest.raises(DataExportError) as error:
        export_snapshot(mapping_file, tmp_path / 'export')
    assert str(error.value) == f'{mapping_file}: mapping must be an object'


def test_export_reports_output_path_errors(tmp_path):
    mapping_file = MAPPING_FILE
    blocked_parent = tmp_path / 'file'
    blocked_parent.write_text('not a directory', encoding='utf-8')
    output = blocked_parent / 'export'

    with pytest.raises(DataExportError) as error:
        export_snapshot(mapping_file, output)
    assert str(error.value).startswith(f'{output}: unable to create output directory:')

    output = tmp_path / 'export'
    output.mkdir()
    blocked_file = output / 'location.csv'
    blocked_file.mkdir()
    with pytest.raises(DataExportError) as error:
        export_snapshot(mapping_file, output)
    assert str(error.value).startswith(f'{blocked_file}: unable to write export:')


@pytest.mark.parametrize(
    ('value', 'expected'),
    [
        (
            datetime(2026, 11, 7, 15, 11, 12, tzinfo=timezone(timedelta(hours=5))),
            '2026-11-07T10:11:12Z',
        ),
        (datetime(2026, 11, 7, 10, 11, 12), '2026-11-07T10:11:12Z'),
    ],
)
def test_export_formats_timestamps_as_utc(value, expected):
    assert _format_value(value) == expected


@pytest.mark.parametrize(
    ('options', 'missing'),
    [
        ({'out': 'export'}, '--mapping'),
        ({'mapping': 'mapping.yaml'}, '--out'),
    ],
)
def test_export_command_requires_mapping_and_output(options, missing):
    with pytest.raises(CommandError, match=rf'required: {re.escape(missing)}'):
        call_command('export_data_snapshot', **options)


def test_export_command_help_describes_snapshot_format():
    parser = Command().create_parser('manage.py', 'export_data_snapshot')
    assert 'Export mapped target tables as snapshot-format CSV files.' in parser.format_help()
