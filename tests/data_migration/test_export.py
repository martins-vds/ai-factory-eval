import csv
from io import StringIO
from pathlib import Path

import pytest
import yaml
from django.core.management import call_command
from django.core.management.base import CommandError

from cargotracker.location.infrastructure.models import LocationRecord

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_SNAPSHOT = PROJECT_ROOT / 'tests/data_migration/fixtures/DM-05C'
MAPPING = PROJECT_ROOT / '.migration/data/mapping.yaml'


def _export_fixture(out, stdout=None):
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(MAPPING),
    )
    call_command(
        'export_data_snapshot',
        mapping=str(MAPPING),
        out=str(out),
        stdout=stdout,
    )


@pytest.mark.django_db(transaction=True)
def test_export_round_trips_fixture_and_preserves_null_and_empty_string(tmp_path):
    out = tmp_path / 'nested' / 'target'
    output = StringIO()
    _export_fixture(out, stdout=output)
    assert output.getvalue() == 'Exported 7 rows across 6 mapped tables.\n'

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
                'misdirected': 'True',
                'eta': '2026-12-29',
                'next_expected_handling_event_type': 'LOAD',
                'next_expected_location_id': r'\N',
                'next_expected_voyage_id': r'\N',
                'unloaded_at_dest': 'False',
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
    for table, rows in expected.items():
        with (out / f'{table}.csv').open(newline='', encoding='utf-8') as stream:
            assert list(csv.DictReader(stream)) == rows

    with (out / 'cargo.csv').open(newline='', encoding='utf-8') as stream:
        cargo = next(csv.DictReader(stream))
    assert cargo['last_known_location_id'] == r'\N'
    with (out / 'voyage.csv').open(newline='', encoding='utf-8') as stream:
        voyage = next(csv.DictReader(stream))
    assert voyage['voyage_number'] == ''

    call_command(
        'export_data_snapshot',
        mapping=str(MAPPING),
        out=str(out),
        stdout=StringIO(),
    )


@pytest.mark.django_db(transaction=True)
def test_export_orders_rows_by_primary_key(tmp_path):
    _export_fixture(tmp_path / 'target')
    LocationRecord.objects.create(id=100, unlocode='SESTO', name='Stockholm')

    out = tmp_path / 'ordered'
    call_command(
        'export_data_snapshot',
        mapping=str(MAPPING),
        out=str(out),
    )

    with (out / 'location.csv').open(newline='', encoding='utf-8') as stream:
        ids = [row['id'] for row in csv.DictReader(stream)]
    assert ids == ['100', '101', '102']


@pytest.mark.django_db(transaction=True)
def test_export_reports_mapping_errors(tmp_path):
    missing_mapping = tmp_path / 'missing.yaml'
    with pytest.raises(CommandError) as error:
        call_command(
            'export_data_snapshot',
            mapping=str(missing_mapping),
            out=str(tmp_path / 'target'),
        )
    assert str(missing_mapping) in str(error.value)
    assert 'unable to read mapping' in str(error.value)

    invalid_mapping = tmp_path / 'invalid.yaml'
    invalid_mapping.write_text('[invalid]', encoding='utf-8')
    with pytest.raises(CommandError) as error:
        call_command(
            'export_data_snapshot',
            mapping=str(invalid_mapping),
            out=str(tmp_path / 'target'),
        )
    assert str(error.value) == f'{invalid_mapping}: mapping must be an object'


@pytest.mark.django_db(transaction=True)
def test_export_rejects_invalid_timestamp_timezone(tmp_path):
    mapping = yaml.safe_load(MAPPING.read_text(encoding='utf-8'))
    mapping['defaults']['timestamp_tz'] = 'Not/A_Timezone'
    mapping_path = tmp_path / 'mapping.yaml'
    mapping_path.write_text(yaml.safe_dump(mapping), encoding='utf-8')

    with pytest.raises(CommandError) as error:
        call_command(
            'export_data_snapshot',
            mapping=str(mapping_path),
            out=str(tmp_path / 'target'),
        )
    assert str(error.value) == "unknown timestamp timezone 'Not/A_Timezone'"


@pytest.mark.django_db(transaction=True)
def test_export_reports_output_path_errors(tmp_path):
    output_file = tmp_path / 'not-a-directory'
    output_file.write_text('not a directory', encoding='utf-8')

    with pytest.raises(CommandError) as error:
        call_command(
            'export_data_snapshot',
            mapping=str(MAPPING),
            out=str(output_file),
        )
    assert str(output_file) in str(error.value)
    assert 'unable to write export' in str(error.value)
