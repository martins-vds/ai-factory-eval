import csv
from io import StringIO
from pathlib import Path

import pytest
import yaml
from django.core.management import call_command
from django.core.management.base import CommandError

from cargotracker.location.infrastructure.models import LocationRecord

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = ROOT / '.migration' / 'data' / 'mapping.yaml'


def _export_fixture(output):
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(MAPPING),
    )
    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(output))


@pytest.mark.django_db(transaction=True)
def test_export_round_trips_fixture_snapshot(tmp_path, capsys):
    output = tmp_path / 'nested' / 'export'
    _export_fixture(output)
    assert 'Exported 7 rows across 6 mapped tables.' in capsys.readouterr().out

    expected = {
        'location': [
            ['id', 'unlocode', 'name'],
            ['101', 'USNYC', 'New York'],
            ['102', 'NLRTM', 'Rotterdam'],
        ],
        'voyage': [
            ['id', 'voyage_number'],
            ['900', ''],
        ],
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
            [
                'id',
                'type',
                'voyage_id',
                'location_id',
                'completionTime',
                'registration',
                'cargo_id',
            ],
            ['71', 'RECEIVE', '900', '102', '2026-11-07T08:12:13Z', '2026-11-07T10:13:14Z', '13'],
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
            ['81', '2026-11-08T08:00:00Z', '2026-11-09T11:00:00Z', '101', '102', '900', '13'],
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

    assert {path.stem for path in output.glob('*.csv')} == set(expected)
    for target, expected_rows in expected.items():
        with (output / f'{target}.csv').open(newline='', encoding='utf-8') as stream:
            assert list(csv.reader(stream)) == expected_rows


def test_export_rejects_invalid_mapping(tmp_path):
    cases = [
        (['invalid'], 'mapping must be an object'),
        ({'tables': 7}, 'mapping has no tables'),
        ({'tables': []}, 'mapping has no tables'),
        ({'tables': [{'target': None, 'columns': {'id': 'ID'}}]}, 'mapping targets must be unique'),
        (
            {
                'tables': [
                    {'target': 'location', 'columns': {'id': 'ID'}},
                    {'target': 'location', 'columns': {'id': 'ID'}},
                ]
            },
            'mapping targets must be unique',
        ),
        ({'tables': [{'target': r'..\location', 'columns': {'id': 'ID'}}]}, 'invalid target table'),
        (
            {'tables': [{'target': 'missing', 'columns': {'id': 'ID'}}]},
            'no registered Django model',
        ),
        ({'tables': [{'target': 'location', 'columns': {}}]}, 'mapping has no columns'),
        ({'tables': [{'target': 'location', 'columns': []}]}, 'mapping has no columns'),
        (
            {'tables': [{'target': 'location', 'columns': {'missing': 'MISSING'}}]},
            "no target column 'missing'",
        ),
        (
            {'tables': [{'target': 'location', 'columns': {'id': None}}]},
            'mapping must name target and source columns',
        ),
    ]
    for index, (mapping, message) in enumerate(cases):
        mapping_file = tmp_path / f'mapping-{index}.yaml'
        mapping_file.write_text(yaml.safe_dump(mapping), encoding='utf-8')

        with pytest.raises(CommandError) as error:
            call_command(
                'export_data_snapshot',
                mapping=str(mapping_file),
                out=str(tmp_path / 'export'),
            )

        assert message in str(error.value)


def test_export_reports_mapping_read_errors(tmp_path):
    missing_mapping = tmp_path / 'missing.yaml'

    with pytest.raises(CommandError) as error:
        call_command(
            'export_data_snapshot',
            mapping=str(missing_mapping),
            out=str(tmp_path / 'export'),
        )

    assert f'{missing_mapping}: unable to read mapping:' in str(error.value)


def test_export_reports_output_write_errors(tmp_path):
    output = tmp_path / 'not-a-directory'
    output.write_text('file', encoding='utf-8')

    with pytest.raises(CommandError) as error:
        call_command('export_data_snapshot', mapping=str(MAPPING), out=str(output))

    assert f'{output}: unable to write export:' in str(error.value)


def test_export_command_help_and_required_options(capsys):
    with pytest.raises(SystemExit) as help_result:
        call_command('export_data_snapshot', '--help')

    assert help_result.value.code == 0
    assert 'Export mapped target tables as CSV files.' in capsys.readouterr().out

    for arguments, option in (
        (('--out', 'export'), '--mapping'),
        (('--mapping', 'mapping.yaml'), '--out'),
    ):
        with pytest.raises(CommandError) as error:
            call_command('export_data_snapshot', *arguments)

        assert f'required: {option}' in str(error.value)


@pytest.mark.django_db(transaction=True)
def test_export_command_reports_row_counts(tmp_path):
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(MAPPING),
    )
    output = StringIO()

    call_command(
        'export_data_snapshot',
        mapping=str(MAPPING),
        out=str(tmp_path / 'export'),
        stdout=output,
    )

    assert output.getvalue() == 'Exported 7 rows across 6 mapped tables.\n'


@pytest.mark.django_db(transaction=True)
def test_export_orders_rows_by_primary_key(tmp_path):
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(MAPPING),
    )
    LocationRecord.objects.create(pk=204, unlocode='ZZZ02', name='Second')
    LocationRecord.objects.create(pk=203, unlocode='ZZZ01', name='First')
    output = tmp_path / 'export'
    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(output))

    with (output / 'location.csv').open(newline='', encoding='utf-8') as stream:
        ids = [int(row['id']) for row in csv.DictReader(stream)]

    assert ids == [101, 102, 203, 204]
    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(output))


@pytest.mark.django_db(transaction=True)
def test_export_preserves_null_empty_string_and_utc_timestamps(tmp_path):
    output = tmp_path / 'export'
    _export_fixture(output)

    with (output / 'cargo.csv').open(newline='', encoding='utf-8') as stream:
        cargo = next(csv.DictReader(stream))
    with (output / 'voyage.csv').open(newline='', encoding='utf-8') as stream:
        voyage = next(csv.DictReader(stream))

    assert cargo['last_known_location_id'] == r'\N'
    assert voyage['voyage_number'] == ''
    assert cargo['calculated_at'] == '2026-11-07T10:11:12Z'
