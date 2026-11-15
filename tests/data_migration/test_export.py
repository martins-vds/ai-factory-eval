import csv

import pytest
import yaml
from django.core.management import call_command
from test_load import FIXTURE_SNAPSHOT, MAPPING

from cargotracker.location.infrastructure.models import LocationRecord


def _load_fixture(tmp_path):
    mapping = tmp_path / 'mapping.yaml'
    mapping.write_text(yaml.safe_dump(MAPPING), encoding='utf-8')
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(mapping),
    )
    return mapping


def _export_fixture(output, mapping):
    call_command(
        'export_data_snapshot',
        mapping=str(mapping),
        out=str(output),
    )


def _records(path):
    with path.open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))


@pytest.mark.django_db(transaction=True)
def test_export_snapshot_round_trips_fixture_rows_and_preserves_null_and_empty(tmp_path):
    mapping = _load_fixture(tmp_path)
    output = tmp_path / 'export'

    _export_fixture(output, mapping)

    assert {
        'location.csv',
        'voyage.csv',
        'cargo.csv',
        'HandlingEvent.csv',
        'leg.csv',
        'carrier_movement.csv',
    } == {path.name for path in output.glob('*.csv')}

    assert _records(output / 'location.csv') == [
        {'id': '101', 'unlocode': 'USNYC', 'name': 'New York'},
        {'id': '102', 'unlocode': 'NLRTM', 'name': 'Rotterdam'},
    ]
    assert _records(output / 'voyage.csv') == [{'id': '900', 'voyage_number': ''}]
    assert _records(output / 'cargo.csv') == [
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
    ]
    assert _records(output / 'HandlingEvent.csv') == [
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
    assert _records(output / 'leg.csv') == [
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
    assert _records(output / 'carrier_movement.csv') == [
        {
            'id': '91',
            'arrival_time': '2026-11-09T10:00:00Z',
            'departure_time': '2026-11-08T12:00:00Z',
            'arrival_location_id': '102',
            'departure_location_id': '101',
            'voyage_id': '900',
        }
    ]


@pytest.mark.django_db(transaction=True)
def test_export_snapshot_orders_rows_by_primary_key(tmp_path):
    mapping = _load_fixture(tmp_path)
    LocationRecord.objects.create(id=104, unlocode='TST04', name='Fourth')
    LocationRecord.objects.create(id=103, unlocode='TST03', name='Third')
    output = tmp_path / 'export'

    _export_fixture(output, mapping)

    assert [row['id'] for row in _records(output / 'location.csv')] == [
        '101',
        '102',
        '103',
        '104',
    ]
