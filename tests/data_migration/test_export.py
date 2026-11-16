import csv
import datetime
from io import StringIO
from pathlib import Path

import pytest
import yaml
from django.core.management import call_command
from django.core.management.base import CommandError

from cargotracker.data_migration.exporter import _format_value
from cargotracker.voyage.infrastructure.models import VoyageRecord

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = ROOT / '.migration' / 'data' / 'mapping.yaml'


def _export_fixture(tmp_path):
    output = tmp_path / 'nested' / 'export'
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(MAPPING),
    )
    command_output = StringIO()
    call_command(
        'export_data_snapshot',
        mapping=str(MAPPING),
        out=str(output),
        stdout=command_output,
    )
    assert command_output.getvalue() == 'Exported 7 rows across 6 mapped tables.\n'
    return output


@pytest.mark.django_db(transaction=True)
def test_export_snapshot_round_trips_fixture_rows(tmp_path):
    output = _export_fixture(tmp_path)
    mapping = yaml.safe_load(MAPPING.read_text(encoding='utf-8'))
    assert {path.name for path in output.glob('*.csv')} == {
        f'{table["target"]}.csv' for table in mapping['tables']
    }

    expected = {
        'location': [
            {'id': '101', 'unlocode': 'USNYC', 'name': 'New York'},
            {'id': '102', 'unlocode': 'NLRTM', 'name': 'Rotterdam'},
        ],
        'voyage': [{'id': '900', 'voyage_number': ''}],
        'cargo': [
            {
                'id': '13',
                'tracking_id': 'FIDELITY-0001',
                'origin_id': '101',
                'spec_origin_id': '101',
                'spec_destination_id': '102',
                'spec_arrival_deadline': '2026-12-30',
                'transport_status': 'NOT_RECEIVED',
                'last_known_location_id': r'\N',
                'current_voyage_id': '900',
                'misdirected': 'true',
                'eta': '2026-12-29',
                'next_expected_handling_event_type': 'LOAD',
                'next_expected_location_id': r'\N',
                'next_expected_voyage_id': r'\N',
                'unloaded_at_dest': 'false',
                'routing_status': 'ROUTED',
                'calculated_at': '2026-11-07T10:11:12Z',
                'last_event_id': '71',
            }
        ],
        'HandlingEvent': [
            {
                'id': '71',
                'type': 'RECEIVE',
                'voyage_id': '900',
                'location_id': '102',
                'completionTime': '2026-11-07T08:12:13Z',
                'registration': '2026-11-07T10:13:14Z',
                'cargo_id': '13',
            }
        ],
        'leg': [
            {
                'id': '81',
                'load_time': '2026-11-08T08:00:00Z',
                'unload_time': '2026-11-09T11:00:00Z',
                'load_location_id': '101',
                'unload_location_id': '102',
                'voyage_id': '900',
                'cargo_id': '13',
            }
        ],
        'carrier_movement': [
            {
                'id': '91',
                'arrival_time': '2026-11-09T10:00:00Z',
                'departure_time': '2026-11-08T12:00:00Z',
                'arrival_location_id': '102',
                'departure_location_id': '101',
                'voyage_id': '900',
            }
        ],
    }
    assert set(expected) == {table['target'] for table in mapping['tables']}
    for table, rows in expected.items():
        with (output / f'{table}.csv').open(newline='', encoding='utf-8') as stream:
            assert list(csv.DictReader(stream)) == rows


@pytest.mark.django_db(transaction=True)
def test_export_snapshot_preserves_null_empty_string_and_utc_timestamp(tmp_path):
    output = _export_fixture(tmp_path)

    with (output / 'cargo.csv').open(newline='', encoding='utf-8') as stream:
        cargo = next(csv.DictReader(stream))
    with (output / 'voyage.csv').open(newline='', encoding='utf-8') as stream:
        voyage = next(csv.DictReader(stream))

    assert cargo['last_known_location_id'] == r'\N'
    assert voyage['voyage_number'] == ''
    assert cargo['calculated_at'] == '2026-11-07T10:11:12Z'


@pytest.mark.django_db(transaction=True)
def test_export_snapshot_orders_rows_by_primary_key(tmp_path):
    VoyageRecord.objects.create(id=20, voyage_number='V020')
    VoyageRecord.objects.create(id=10, voyage_number='V010')
    mapping = yaml.safe_load(MAPPING.read_text(encoding='utf-8'))
    mapping['tables'] = [mapping['tables'][1]]
    mapping_path = tmp_path / 'mapping.yaml'
    mapping_path.write_text(yaml.safe_dump(mapping), encoding='utf-8')
    output = tmp_path / 'export'

    call_command('export_data_snapshot', mapping=str(mapping_path), out=str(output))

    with (output / 'voyage.csv').open(newline='', encoding='utf-8') as stream:
        rows = list(csv.DictReader(stream))
    assert [row['id'] for row in rows] == ['10', '20']


@pytest.mark.django_db(transaction=True)
def test_export_snapshot_can_replace_an_existing_export(tmp_path):
    output = _export_fixture(tmp_path)
    original = {path.name: path.read_bytes() for path in output.glob('*.csv')}

    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(output))

    assert {path.name: path.read_bytes() for path in output.glob('*.csv')} == original


def test_export_snapshot_requires_both_arguments(tmp_path):
    with pytest.raises(CommandError, match='the following arguments are required: --mapping'):
        call_command('export_data_snapshot', '--out', str(tmp_path))
    with pytest.raises(CommandError, match='the following arguments are required: --out'):
        call_command('export_data_snapshot', '--mapping', str(MAPPING))


def test_export_snapshot_reports_invalid_mapping(tmp_path):
    mapping = tmp_path / 'mapping.yaml'
    mapping.write_text('- invalid', encoding='utf-8')

    with pytest.raises(CommandError, match='mapping must be an object'):
        call_command(
            'export_data_snapshot',
            mapping=str(mapping),
            out=str(tmp_path / 'export'),
        )


def test_export_snapshot_reports_unreadable_mapping(tmp_path):
    mapping = tmp_path / 'missing.yaml'

    with pytest.raises(CommandError, match='unable to read mapping'):
        call_command(
            'export_data_snapshot',
            mapping=str(mapping),
            out=str(tmp_path / 'export'),
        )


def test_export_snapshot_reports_output_write_errors(tmp_path):
    output = tmp_path / 'not-a-directory'
    output.write_text('file', encoding='utf-8')

    with pytest.raises(CommandError, match='unable to write export'):
        call_command('export_data_snapshot', mapping=str(MAPPING), out=str(output))


def test_export_formats_naive_and_offset_timestamps_as_utc():
    assert _format_value(datetime.datetime(2026, 11, 7, 10, 11, 12)) == (
        '2026-11-07T10:11:12Z'
    )
    offset_timestamp = datetime.datetime(
        2026,
        11,
        7,
        10,
        11,
        12,
        tzinfo=datetime.timezone(datetime.timedelta(hours=2)),
    )
    assert _format_value(offset_timestamp) == '2026-11-07T08:11:12Z'
