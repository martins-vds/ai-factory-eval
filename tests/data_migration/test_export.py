import csv
from pathlib import Path

import pytest
from django.core.management import call_command

from cargotracker.location.infrastructure.models import LocationRecord

FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = Path(__file__).parents[2] / '.migration' / 'data' / 'mapping.yaml'


@pytest.mark.django_db(transaction=True)
def test_export_round_trips_snapshot_fixture(tmp_path):
    call_command('load_data_snapshot', snapshot=str(FIXTURE_SNAPSHOT), mapping=str(MAPPING))
    exported = tmp_path / 'target'

    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(exported))

    expected_rows = {
        'location': [
            ['101', 'USNYC', 'New York'],
            ['102', 'NLRTM', 'Rotterdam'],
        ],
        'voyage': [['900', '']],
        'cargo': [
            [
                '13',
                'FIDELITY-0001',
                '101',
                '101',
                '102',
                '2026-12-30',
                'NOT_RECEIVED',
                '\\N',
                '900',
                'True',
                '2026-12-29',
                'LOAD',
                '\\N',
                '\\N',
                'False',
                'ROUTED',
                '2026-11-07T10:11:12Z',
                '71',
            ],
        ],
        'HandlingEvent': [
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
        'leg': [['81', '2026-11-08T08:00:00Z', '2026-11-09T11:00:00Z', '101', '102', '900', '13']],
        'carrier_movement': [
            ['91', '2026-11-09T10:00:00Z', '2026-11-08T12:00:00Z', '102', '101', '900'],
        ],
    }
    for table, expected in expected_rows.items():
        with (exported / f'{table}.csv').open(encoding='utf-8', newline='') as stream:
            assert list(csv.reader(stream))[1:] == expected


@pytest.mark.django_db(transaction=True)
def test_export_distinguishes_null_from_empty_string(tmp_path):
    call_command('load_data_snapshot', snapshot=str(FIXTURE_SNAPSHOT), mapping=str(MAPPING))
    LocationRecord.objects.filter(pk=101).update(name='')
    exported = tmp_path / 'target'

    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(exported))

    with (exported / 'cargo.csv').open(encoding='utf-8', newline='') as stream:
        cargo = next(csv.DictReader(stream))
    with (exported / 'location.csv').open(encoding='utf-8', newline='') as stream:
        location = next(csv.DictReader(stream))
    assert cargo['last_known_location_id'] == '\\N'
    assert location['name'] == ''


@pytest.mark.django_db(transaction=True)
def test_export_orders_by_primary_key_and_writes_utc_timestamps(tmp_path):
    call_command('load_data_snapshot', snapshot=str(FIXTURE_SNAPSHOT), mapping=str(MAPPING))
    LocationRecord.objects.create(pk=104, unlocode='ZZZZZ', name='Z')
    LocationRecord.objects.create(pk=103, unlocode='YYYYY', name='Y')
    exported = tmp_path / 'target'

    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(exported))

    with (exported / 'location.csv').open(encoding='utf-8', newline='') as stream:
        locations = list(csv.DictReader(stream))
    with (exported / 'HandlingEvent.csv').open(encoding='utf-8', newline='') as stream:
        event = next(csv.DictReader(stream))
    with (exported / 'cargo.csv').open(encoding='utf-8', newline='') as stream:
        cargo = next(csv.DictReader(stream))
    assert [int(row['id']) for row in locations] == [101, 102, 103, 104]
    assert event['completionTime'] == '2026-11-07T08:12:13Z'
    assert event['registration'] == '2026-11-07T10:13:14Z'
    assert cargo['calculated_at'] == '2026-11-07T10:11:12Z'
