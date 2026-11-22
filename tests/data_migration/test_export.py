import csv
import re
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import pytest
import yaml
from django.core.management import call_command
from django.core.management.base import CommandError

from cargotracker.location.infrastructure.models import LocationRecord

REPOSITORY_ROOT = Path(__file__).parents[2]
FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = REPOSITORY_ROOT / '.migration' / 'data' / 'mapping.yaml'

EXPECTED_EXPORTS = {
    'location': [
        ['id', 'unlocode', 'name'],
        ['101', 'USNYC', 'New York'],
        ['102', 'NLRTM', 'Rotterdam'],
    ],
    'voyage': [['id', 'voyage_number'], ['900', '']],
    'cargo': [
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
        ],
    ],
    'HandlingEvent': [
        ['id', 'type', 'voyage_id', 'location_id', 'completionTime', 'registration', 'cargo_id'],
        [
            '71',
            'RECEIVE',
            '900',
            '102',
            '2026-11-07T08:12:13Z',
            '2026-11-07T10:13:14Z',
            '13',
        ],
    ],
    'leg': [
        [
            'id',
            'load_time',
            'unload_time',
            'load_location_id',
            'unload_location_id',
            'voyage_id',
            'cargo_id',
        ],
        [
            '81',
            '2026-11-08T08:00:00Z',
            '2026-11-09T11:00:00Z',
            '101',
            '102',
            '900',
            '13',
        ],
    ],
    'carrier_movement': [
        [
            'id',
            'arrival_time',
            'departure_time',
            'arrival_location_id',
            'departure_location_id',
            'voyage_id',
        ],
        ['91', '2026-11-09T10:00:00Z', '2026-11-08T12:00:00Z', '102', '101', '900'],
    ],
}


def _load_fixture(mapping=MAPPING):
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(mapping),
    )


def _write_mapping(tmp_path, mapping):
    mapping_path = tmp_path / 'mapping.yaml'
    mapping_path.write_text(yaml.safe_dump(mapping), encoding='utf-8')
    return mapping_path


@pytest.mark.django_db(transaction=True)
def test_export_snapshot_round_trips_fixture_and_preserves_null_and_empty(tmp_path):
    _load_fixture()
    output_dir = tmp_path / 'target' / 'nested'
    output = StringIO()
    call_command(
        'export_data_snapshot',
        mapping=str(MAPPING),
        out=str(output_dir),
        stdout=output,
    )

    assert output.getvalue() == 'Exported 7 rows across 6 mapped tables.\n'
    assert sorted(path.name for path in output_dir.glob('*.csv')) == sorted(
        f'{table}.csv' for table in EXPECTED_EXPORTS
    )
    for table, expected in EXPECTED_EXPORTS.items():
        with (output_dir / f'{table}.csv').open(newline='', encoding='utf-8') as stream:
            assert list(csv.reader(stream)) == expected


@pytest.mark.django_db(transaction=True)
def test_export_snapshot_orders_rows_by_primary_key(tmp_path):
    _load_fixture()
    LocationRecord.objects.create(id=100, unlocode='TST00', name='Test')
    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(tmp_path))

    with (tmp_path / 'location.csv').open(newline='', encoding='utf-8') as stream:
        ids = [row['id'] for row in csv.DictReader(stream)]

    assert ids == ['100', '101', '102']


@pytest.mark.django_db(transaction=True)
def test_export_snapshot_converts_mapped_timestamps_to_utc(tmp_path):
    mapping = yaml.safe_load(MAPPING.read_text(encoding='utf-8'))
    mapping['defaults']['timestamp_tz'] = 'Asia/Tokyo'
    mapping_path = _write_mapping(tmp_path, mapping)
    _load_fixture(mapping_path)
    call_command('export_data_snapshot', mapping=str(mapping_path), out=str(tmp_path))

    with (tmp_path / 'cargo.csv').open(newline='', encoding='utf-8') as stream:
        cargo = next(csv.DictReader(stream))

    assert cargo['calculated_at'] == '2026-11-07T01:11:12Z'


@pytest.mark.parametrize(
    ('mapping', 'message'),
    [
        ({'tables': []}, 'mapping has no tables'),
        ({'tables': 'location'}, 'mapping has no tables'),
        ({'tables': [{'target': None, 'columns': {'id': 'ID'}}]}, 'mapping targets must be unique'),
        ({'tables': [{'target': 17, 'columns': {'id': 'ID'}}]}, 'mapping targets must be unique'),
        (
            {
                'tables': [
                    {'target': 'location', 'columns': {'id': 'ID'}},
                    {'target': 'location', 'columns': {'id': 'ID'}},
                ]
            },
            'mapping targets must be unique',
        ),
        (
            {'tables': [{'target': '..', 'columns': {'id': 'ID'}}]},
            "'..': invalid target table name",
        ),
        (
            {'tables': [{'target': '../location', 'columns': {'id': 'ID'}}]},
            "'../location': invalid target table name",
        ),
        (
            {'tables': [{'target': 'unmapped', 'columns': {'id': 'ID'}}]},
            'unmapped: no registered Django model for target table',
        ),
        (
            {'tables': [{'target': 'location', 'columns': []}]},
            'location: mapping has no columns',
        ),
        (
            {'tables': [{'target': 'location', 'columns': 'id'}]},
            'location: mapping has no columns',
        ),
        (
            {'tables': [{'target': 'location', 'columns': {'missing': 'MISSING'}}]},
            "location: no target column 'missing'",
        ),
        (
            {'tables': [{'target': 'location', 'columns': {'name': 'NAME'}}]},
            'location: mapping must include its primary key',
        ),
    ],
    ids=[
        'no_tables_empty',
        'no_tables_wrong_type',
        'target_none',
        'target_non_string',
        'target_duplicate',
        'target_parent_path',
        'target_path',
        'unknown_model',
        'empty_columns',
        'columns_wrong_type',
        'unknown_column',
        'missing_primary_key',
    ],
)
def test_export_snapshot_rejects_invalid_mapping(tmp_path, mapping, message):
    mapping_path = _write_mapping(tmp_path, mapping)

    with pytest.raises(CommandError, match=f'^{re.escape(message)}'):
        call_command(
            'export_data_snapshot',
            mapping=str(mapping_path),
            out=str(tmp_path / 'target'),
        )


@pytest.mark.parametrize(
    ('mapping', 'message'),
    [
        ('not: [valid', 'unable to read mapping:'),
        ('not a mapping', 'mapping must be an object'),
    ],
    ids=['yaml_syntax', 'yaml_scalar'],
)
def test_export_snapshot_reports_invalid_mapping_files(tmp_path, mapping, message):
    mapping_path = tmp_path / 'mapping.yaml'
    mapping_path.write_text(mapping, encoding='utf-8')

    with pytest.raises(CommandError, match=f'^{re.escape(f"{mapping_path}: {message}")}'):
        call_command(
            'export_data_snapshot',
            mapping=str(mapping_path),
            out=str(tmp_path / 'target'),
        )


@pytest.mark.parametrize(
    ('defaults', 'message'),
    [
        ('UTC', 'mapping defaults must be an object'),
        ({'timestamp_tz': 'Not/A_Timezone'}, "unknown timestamp timezone 'Not/A_Timezone'"),
    ],
    ids=['defaults_type', 'timezone_name'],
)
def test_export_snapshot_rejects_invalid_timestamp_defaults(tmp_path, defaults, message):
    mapping_path = _write_mapping(tmp_path, {'defaults': defaults, 'tables': []})

    with pytest.raises(CommandError, match=f'^{re.escape(message)}'):
        call_command(
            'export_data_snapshot',
            mapping=str(mapping_path),
            out=str(tmp_path / 'target'),
        )


def test_export_snapshot_requires_mapping_file(tmp_path):
    mapping_path = tmp_path / 'missing.yaml'

    with pytest.raises(
        CommandError,
        match=f'^{re.escape(f"{mapping_path}: unable to read mapping:")}',
    ):
        call_command(
            'export_data_snapshot',
            mapping=str(mapping_path),
            out=str(tmp_path / 'target'),
        )


@pytest.mark.django_db(transaction=True)
def test_export_snapshot_reports_output_directory_errors(tmp_path):
    output_file = tmp_path / 'not-a-directory'
    output_file.write_text('occupied', encoding='utf-8')

    with pytest.raises(
        CommandError,
        match=f'^{re.escape(f"{output_file}: unable to create output directory:")}',
    ):
        call_command(
            'export_data_snapshot',
            mapping=str(MAPPING),
            out=str(output_file),
        )


@pytest.mark.django_db(transaction=True)
def test_export_snapshot_reports_table_write_errors(tmp_path):
    _load_fixture()
    (tmp_path / 'cargo.csv').mkdir()

    with pytest.raises(
        CommandError,
        match=f'^{re.escape(f"{tmp_path}/cargo.csv: unable to write export:")}',
    ):
        call_command('export_data_snapshot', mapping=str(MAPPING), out=str(tmp_path))


@pytest.mark.parametrize(
    ('options', 'missing'),
    [
        ({'out': 'output'}, '--mapping'),
        ({'mapping': str(MAPPING)}, '--out'),
    ],
    ids=['mapping_required', 'out_required'],
)
def test_export_command_requires_mapping_and_output(options, missing):
    with pytest.raises(
        CommandError,
        match=f'^{re.escape(f"Error: the following arguments are required: {missing}")}',
    ):
        call_command('export_data_snapshot', **options)


def test_export_command_describes_its_purpose():
    output = StringIO()
    with redirect_stdout(output), pytest.raises(SystemExit) as help_exit:
        call_command('export_data_snapshot', '--help')

    assert help_exit.value.code == 0
    assert 'Export mapped target tables as a relational snapshot.' in output.getvalue()
