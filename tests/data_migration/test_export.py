import csv
from pathlib import Path

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

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
    output = tmp_path / 'nested' / 'target'

    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(output))
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


@pytest.mark.parametrize(
    ('options', 'missing_option'),
    [
        ({'out': 'target'}, '--mapping'),
        ({'mapping': str(MAPPING)}, '--out'),
    ],
)
def test_export_command_requires_mapping_and_output(options, missing_option):
    with pytest.raises(CommandError, match=f'required: {missing_option}'):
        call_command('export_data_snapshot', **options)


def test_export_command_rejects_non_object_mapping(tmp_path):
    mapping = tmp_path / 'mapping.yaml'
    mapping.write_text('[]', encoding='utf-8')

    with pytest.raises(CommandError) as error:
        call_command('export_data_snapshot', mapping=str(mapping), out=str(tmp_path / 'target'))

    assert str(error.value) == f'{mapping}: mapping must be an object'
