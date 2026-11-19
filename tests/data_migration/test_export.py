import csv
from io import StringIO
from pathlib import Path

import pytest
import yaml
from django.core.management import call_command
from django.core.management.base import CommandError

from cargotracker.location.infrastructure.models import LocationRecord

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = REPOSITORY_ROOT / '.migration' / 'data' / 'mapping.yaml'


def _read_csv(path):
    with path.open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))


def _write_mapping(directory, mapping):
    path = directory / 'mapping.yaml'
    path.write_text(yaml.safe_dump(mapping), encoding='utf-8')
    return path


@pytest.mark.django_db(transaction=True)
def test_export_data_snapshot_round_trips_fixture_rows_and_preserves_nulls(tmp_path):
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(MAPPING),
    )
    output = tmp_path / 'nested' / 'export'
    stdout = StringIO()

    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(output), stdout=stdout)
    assert stdout.getvalue() == 'Exported 7 rows across 6 mapped tables.\n'
    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(output))

    assert {path.name for path in output.glob('*.csv')} == {
        'location.csv',
        'voyage.csv',
        'cargo.csv',
        'HandlingEvent.csv',
        'leg.csv',
        'carrier_movement.csv',
    }

    assert _read_csv(output / 'location.csv') == [
        {'id': '101', 'unlocode': 'USNYC', 'name': 'New York'},
        {'id': '102', 'unlocode': 'NLRTM', 'name': 'Rotterdam'},
    ]
    assert _read_csv(output / 'voyage.csv') == [{'id': '900', 'voyage_number': ''}]
    assert _read_csv(output / 'cargo.csv') == [
        {
            'id': '13',
            'tracking_id': 'FIDELITY-0001',
            'origin_id': '101',
            'spec_origin_id': '101',
            'spec_destination_id': '102',
            'spec_arrival_deadline': '2026-12-30',
            'transport_status': 'NOT_RECEIVED',
            'last_known_location_id': '\\N',
            'current_voyage_id': '900',
            'misdirected': 'true',
            'eta': '2026-12-29',
            'next_expected_handling_event_type': 'LOAD',
            'next_expected_location_id': '\\N',
            'next_expected_voyage_id': '\\N',
            'unloaded_at_dest': 'false',
            'routing_status': 'ROUTED',
            'calculated_at': '2026-11-07T10:11:12Z',
            'last_event_id': '71',
        }
    ]
    assert _read_csv(output / 'HandlingEvent.csv') == [
        {
            'id': '71',
            'type': 'RECEIVE',
            'voyage_id': '900',
            'location_id': '102',
            'completionTime': '2026-11-07T08:12:13Z',
            'registration': '2026-11-07T10:13:14Z',
            'cargo_id': '13',
        }
    ]
    assert _read_csv(output / 'leg.csv') == [
        {
            'id': '81',
            'load_time': '2026-11-08T08:00:00Z',
            'unload_time': '2026-11-09T11:00:00Z',
            'load_location_id': '101',
            'unload_location_id': '102',
            'voyage_id': '900',
            'cargo_id': '13',
        }
    ]
    assert _read_csv(output / 'carrier_movement.csv') == [
        {
            'id': '91',
            'arrival_time': '2026-11-09T10:00:00Z',
            'departure_time': '2026-11-08T12:00:00Z',
            'arrival_location_id': '102',
            'departure_location_id': '101',
            'voyage_id': '900',
        }
    ]

    cargo = _read_csv(output / 'cargo.csv')[0]
    voyage = _read_csv(output / 'voyage.csv')[0]
    assert cargo['last_known_location_id'] == '\\N'
    assert voyage['voyage_number'] == ''


@pytest.mark.django_db(transaction=True)
def test_export_data_snapshot_orders_rows_by_primary_key(tmp_path):
    LocationRecord.objects.create(id=20, unlocode='TST20', name='Later')
    LocationRecord.objects.create(id=10, unlocode='TST10', name='Earlier')

    output = tmp_path / 'export'
    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(output))

    locations = _read_csv(output / 'location.csv')
    assert [row['id'] for row in locations] == ['10', '20']


def test_export_rejects_invalid_mappings(tmp_path):
    invalid_mappings = [
        ({'tables': {'location': {}}}, 'mapping has no tables'),
        ({'tables': [None]}, 'each mapped table must be an object'),
        (
            {'tables': [{'target': 'missing', 'columns': {'id': 'ID'}}]},
            'missing: no registered Django model for target table',
        ),
        (
            {'tables': [{'target': 'location', 'columns': {}}]},
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
        (
            {
                'tables': [
                    {'target': 'location', 'columns': {'id': 'ID'}},
                    {'target': 'location', 'columns': {'id': 'ID'}},
                ]
            },
            'mapping targets must be unique table names',
        ),
    ]
    for mapping, message in invalid_mappings:
        mapping_file = _write_mapping(tmp_path, mapping)
        with pytest.raises(CommandError) as error:
            call_command(
                'export_data_snapshot',
                mapping=str(mapping_file),
                out=str(tmp_path / 'export'),
            )

        assert str(error.value) == message


def test_export_reports_mapping_file_errors(tmp_path):
    missing_file = tmp_path / 'missing.yaml'

    with pytest.raises(CommandError) as missing_error:
        call_command(
            'export_data_snapshot',
            mapping=str(missing_file),
            out=str(tmp_path / 'export'),
        )
    assert str(missing_error.value).startswith(f'{missing_file}: unable to read mapping:')

    invalid_file = tmp_path / 'invalid.yaml'
    invalid_file.write_text('[]', encoding='utf-8')
    with pytest.raises(CommandError) as invalid_error:
        call_command(
            'export_data_snapshot',
            mapping=str(invalid_file),
            out=str(tmp_path / 'export'),
        )
    assert str(invalid_error.value) == f'{invalid_file}: mapping must be an object'


def test_export_requires_mapping_and_output_arguments():
    with pytest.raises(CommandError, match='required'):
        call_command('export_data_snapshot', mapping=str(MAPPING))
    with pytest.raises(CommandError, match='required'):
        call_command('export_data_snapshot', out='export')


def test_export_command_help_describes_csv_exports(capsys):
    with pytest.raises(SystemExit) as exit_error:
        call_command('export_data_snapshot', '--help')

    assert exit_error.value.code == 0
    output = capsys.readouterr().out
    assert output.startswith('usage:')
    assert 'Export mapped target tables as CSV files.' in output.splitlines()


def test_export_reports_output_directory_errors(tmp_path):
    mapping_file = _write_mapping(
        tmp_path,
        {'tables': [{'target': 'location', 'columns': {'id': 'ID'}}]},
    )
    output_parent = tmp_path / 'not-a-directory'
    output_parent.write_text('file', encoding='utf-8')

    with pytest.raises(CommandError) as error:
        call_command(
            'export_data_snapshot',
            mapping=str(mapping_file),
            out=str(output_parent / 'export'),
        )

    assert str(error.value).startswith(f'{output_parent / "export"}: unable to write export:')
