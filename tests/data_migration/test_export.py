import csv
from pathlib import Path

import pytest
from django.core.management import call_command

from cargotracker.location.infrastructure.models import LocationRecord

ROOT = Path(__file__).parents[2]
FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = ROOT / '.migration' / 'data' / 'mapping.yaml'


@pytest.mark.django_db(transaction=True)
def test_export_snapshot_round_trips_fixture_rows_and_preserves_nulls(tmp_path):
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(MAPPING),
    )
    LocationRecord.objects.create(id=100, unlocode='AUSYD', name='Sydney')
    output = tmp_path / 'target'

    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(output))

    assert {path.stem for path in output.glob('*.csv')} == {
        'location',
        'voyage',
        'cargo',
        'HandlingEvent',
        'leg',
        'carrier_movement',
    }

    with (output / 'location.csv').open(newline='', encoding='utf-8') as stream:
        assert list(csv.reader(stream)) == [
            ['id', 'unlocode', 'name'],
            ['100', 'AUSYD', 'Sydney'],
            ['101', 'USNYC', 'New York'],
            ['102', 'NLRTM', 'Rotterdam'],
        ]

    with (output / 'voyage.csv').open(newline='', encoding='utf-8') as stream:
        voyage_rows = list(csv.DictReader(stream))
    assert voyage_rows == [{'id': '900', 'voyage_number': ''}]

    with (output / 'cargo.csv').open(newline='', encoding='utf-8') as stream:
        cargo = next(csv.DictReader(stream))
    assert cargo['last_known_location_id'] == r'\N'
    assert cargo['next_expected_location_id'] == r'\N'
    assert cargo['calculated_at'] == '2026-11-07T10:11:12Z'
