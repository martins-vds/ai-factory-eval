import csv
from datetime import datetime, timedelta, timezone
from io import StringIO
from pathlib import Path

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
import yaml

from cargotracker.handling.infrastructure.models import HandlingEventRecord

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = ROOT / '.migration' / 'data' / 'mapping.yaml'


@pytest.mark.django_db(transaction=True)
def test_export_data_snapshot_round_trips_fixture_rows(tmp_path, capsys):
    call_command('load_data_snapshot', snapshot=str(FIXTURE_SNAPSHOT), mapping=str(MAPPING))
    capsys.readouterr()
    output = tmp_path / 'nested' / 'export'

    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(output))
    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(output))

    expected_tables = {
        'location.csv': [
            ['id', 'unlocode', 'name'],
            ['101', 'USNYC', 'New York'],
            ['102', 'NLRTM', 'Rotterdam'],
        ],
        'voyage.csv': [
            ['id', 'voyage_number'],
            ['900', ''],
        ],
        'cargo.csv': [
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
                'True',
                '2026-12-29',
                'LOAD',
                r'\N',
                r'\N',
                'False',
                'ROUTED',
                '2026-11-07T10:11:12Z',
                '71',
            ],
        ],
        'HandlingEvent.csv': [
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
        'leg.csv': [
            [
                'id',
                'load_time',
                'unload_time',
                'load_location_id',
                'unload_location_id',
                'voyage_id',
                'cargo_id',
            ],
            ['81', '2026-11-08T08:00:00Z', '2026-11-09T11:00:00Z', '101', '102', '900', '13'],
        ],
        'carrier_movement.csv': [
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
    assert {path.name for path in output.glob('*.csv')} == set(expected_tables)
    for filename, expected_rows in expected_tables.items():
        with (output / filename).open(newline='', encoding='utf-8') as stream:
            assert list(csv.reader(stream)) == expected_rows
    assert capsys.readouterr().out.splitlines() == [
        'Exported 7 rows across 6 mapped tables.',
        'Exported 7 rows across 6 mapped tables.',
    ]


@pytest.mark.django_db(transaction=True)
def test_export_data_snapshot_preserves_null_empty_string_and_utc_order(tmp_path):
    call_command('load_data_snapshot', snapshot=str(FIXTURE_SNAPSHOT), mapping=str(MAPPING))
    offset = timezone(timedelta(hours=2))
    for event_id, event_type in ((73, ''), (72, 'RECEIVE')):
        HandlingEventRecord.objects.create(
            id=event_id,
            event_type=event_type,
            voyage_id=None,
            location_id=102,
            completion_time=datetime(2026, 11, 7, 10, 12, 13, tzinfo=offset),
            registration_time=datetime(2026, 11, 7, 10, 13, 14, tzinfo=offset),
            cargo_id=13,
        )
    output = tmp_path / 'export'

    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(output))

    with (output / 'HandlingEvent.csv').open(newline='', encoding='utf-8') as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)

    assert [row['id'] for row in rows] == ['71', '72', '73']
    empty_value = rows[-1]
    assert empty_value['type'] == ''
    assert empty_value['voyage_id'] == r'\N'
    assert empty_value['completionTime'] == '2026-11-07T08:12:13Z'


def test_export_data_snapshot_rejects_invalid_mappings(tmp_path):
    cases = [
        ({'tables': 'not-a-list'}, 'mapping has no tables'),
        ({'tables': []}, 'mapping has no tables'),
        ({'tables': [None]}, 'each mapped table must be an object'),
        (
            {'tables': [{'target': None, 'columns': {'id': 'id'}}]},
            'invalid target table name None',
        ),
        (
            {'tables': [{'target': '../location', 'columns': {'id': 'id'}}]},
            "invalid target table name '../location'",
        ),
        (
            {'tables': [{'target': '..\\location', 'columns': {'id': 'id'}}]},
            r"invalid target table name '..\\location'",
        ),
        (
            {'tables': [{'target': 'missing_model', 'columns': {'id': 'id'}}]},
            'missing_model: no registered Django model for target table',
        ),
        (
            {'tables': [{'target': 'location', 'columns': 'not-a-mapping'}]},
            'location: mapping has no columns',
        ),
        (
            {'tables': [{'target': 'location', 'columns': {}}]},
            'location: mapping has no columns',
        ),
        (
            {'tables': [{'target': 'location', 'columns': {1: 'id'}}]},
            'location: mapped target columns must be strings',
        ),
        (
            {'tables': [{'target': 'location', 'columns': {'unknown': 'unknown'}}]},
            "location: no target column 'unknown'",
        ),
        (
            {'tables': [{'target': 'location', 'columns': {'unlocode': 'unlocode'}}]},
            'location: mapping must include its primary key',
        ),
        (
            {
                'tables': [
                    {'target': 'location', 'columns': {'id': 'id'}},
                    {'target': 'location', 'columns': {'id': 'id'}},
                ]
            },
            'mapping targets must be unique table names: location',
        ),
    ]
    for index, (mapping, expected_error) in enumerate(cases):
        mapping_path = tmp_path / f'mapping-{index}.yaml'
        mapping_path.write_text(yaml.safe_dump(mapping), encoding='utf-8')

        with pytest.raises(CommandError) as error:
            call_command(
                'export_data_snapshot',
                mapping=str(mapping_path),
                out=str(tmp_path / 'export'),
            )

        assert str(error.value) == expected_error


def test_export_data_snapshot_reports_mapping_file_errors(tmp_path):
    mapping_path = tmp_path / 'missing.yaml'
    with pytest.raises(CommandError) as missing_error:
        call_command('export_data_snapshot', mapping=str(mapping_path), out=str(tmp_path / 'export'))
    assert str(missing_error.value).startswith(f'{mapping_path}: unable to read mapping: ')

    mapping_path.write_text('[]', encoding='utf-8')
    with pytest.raises(CommandError) as shape_error:
        call_command('export_data_snapshot', mapping=str(mapping_path), out=str(tmp_path / 'export'))
    assert str(shape_error.value) == f'{mapping_path}: mapping must be an object'


def test_export_data_snapshot_requires_arguments_and_describes_command(tmp_path, capsys):
    for options, missing in (
        ({'mapping': str(MAPPING)}, '--out'),
        ({'out': str(tmp_path / 'export')}, '--mapping'),
    ):
        with pytest.raises(CommandError) as error:
            call_command('export_data_snapshot', **options)
        assert missing in str(error.value)

    output = StringIO()
    with pytest.raises(SystemExit) as help_exit:
        call_command('export_data_snapshot', '--help', stdout=output)
    assert help_exit.value.code == 0
    assert 'Export mapped target tables as a relational snapshot.' in capsys.readouterr().out


@pytest.mark.django_db(transaction=True)
def test_export_data_snapshot_reports_output_errors(tmp_path):
    output = tmp_path / 'file'
    output.write_text('not a directory', encoding='utf-8')

    with pytest.raises(CommandError) as error:
        call_command('export_data_snapshot', mapping=str(MAPPING), out=str(output))

    assert str(error.value).startswith(f'{output}: unable to write export: ')
