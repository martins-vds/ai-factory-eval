import csv
from io import StringIO
from pathlib import Path

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from cargotracker.location.infrastructure.models import LocationRecord

FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = Path(__file__).parents[2] / '.migration' / 'data' / 'mapping.yaml'


@pytest.mark.django_db(transaction=True)
def test_export_data_snapshot_round_trips_mapped_fixture(tmp_path):
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(MAPPING),
    )
    output = tmp_path / 'nested' / 'target'
    command_output = StringIO()

    call_command(
        'export_data_snapshot',
        mapping=str(MAPPING),
        out=str(output),
        stdout=command_output,
    )
    assert command_output.getvalue() == 'Exported 7 rows across 6 mapped tables.\n'

    before = {path.name: path.read_bytes() for path in output.glob('*.csv')}
    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(output))
    assert {path.name: path.read_bytes() for path in output.glob('*.csv')} == before

    assert {path.name for path in output.glob('*.csv')} == {
        'location.csv',
        'voyage.csv',
        'cargo.csv',
        'HandlingEvent.csv',
        'leg.csv',
        'carrier_movement.csv',
    }

    def rows(table):
        with (output / f'{table}.csv').open(newline='', encoding='utf-8') as stream:
            return list(csv.reader(stream))

    assert rows('location') == [
        ['id', 'unlocode', 'name'],
        ['101', 'USNYC', 'New York'],
        ['102', 'NLRTM', 'Rotterdam'],
    ]
    assert rows('voyage') == [
        ['id', 'voyage_number'],
        ['900', ''],
    ]
    assert rows('cargo') == [
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
    ]
    assert rows('HandlingEvent') == [
        [
            'id',
            'type',
            'voyage_id',
            'location_id',
            'completionTime',
            'registration',
            'cargo_id',
        ],
        [
            '71',
            'RECEIVE',
            '900',
            '102',
            '2026-11-07T08:12:13Z',
            '2026-11-07T10:13:14Z',
            '13',
        ],
    ]
    assert rows('leg') == [
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
    ]
    assert rows('carrier_movement') == [
        [
            'id',
            'arrival_time',
            'departure_time',
            'arrival_location_id',
            'departure_location_id',
            'voyage_id',
        ],
        [
            '91',
            '2026-11-09T10:00:00Z',
            '2026-11-08T12:00:00Z',
            '102',
            '101',
            '900',
        ],
    ]


@pytest.mark.django_db(transaction=True)
def test_export_orders_rows_by_primary_key(tmp_path):
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(MAPPING),
    )
    LocationRecord.objects.create(id=100, unlocode='TST00', name='Test location')
    output = tmp_path / 'target'

    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(output))

    with (output / 'location.csv').open(newline='', encoding='utf-8') as stream:
        rows = list(csv.reader(stream))
    assert [row[0] for row in rows[1:]] == ['100', '101', '102']


@pytest.mark.parametrize('provided', [{'out': 'unused'}, {'mapping': 'unused'}])
def test_export_requires_mapping_and_output_directory(provided):
    with pytest.raises(CommandError):
        call_command('export_data_snapshot', **provided)
