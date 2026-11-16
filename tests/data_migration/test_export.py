import csv
from datetime import UTC, datetime
from io import StringIO
from pathlib import Path

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from cargotracker.location.infrastructure.models import LocationRecord

FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = Path(__file__).parents[2] / '.migration' / 'data' / 'mapping.yaml'


def _read_csv(path):
    with path.open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))


@pytest.mark.django_db(transaction=True)
def test_export_snapshot_round_trips_fixture_rows(tmp_path):
    call_command('load_data_snapshot', snapshot=str(FIXTURE_SNAPSHOT), mapping=str(MAPPING))
    LocationRecord.objects.create(pk=200, unlocode='ZZ200', name='Later')
    LocationRecord.objects.create(pk=150, unlocode='ZZ150', name='Earlier')

    for options in (
        {'out': str(tmp_path / 'missing-mapping')},
        {'mapping': str(MAPPING)},
    ):
        with pytest.raises(CommandError, match='required'):
            call_command('export_data_snapshot', **options)

    output = tmp_path / 'nested' / 'target'
    stdout = StringIO()
    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(output), stdout=stdout)
    assert stdout.getvalue() == 'Exported 9 rows across 6 mapped tables.\n'

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
        {'id': '150', 'unlocode': 'ZZ150', 'name': 'Earlier'},
        {'id': '200', 'unlocode': 'ZZ200', 'name': 'Later'},
    ]
    assert _read_csv(output / 'voyage.csv') == [
        {'id': '900', 'voyage_number': ''},
    ]

    cargo = _read_csv(output / 'cargo.csv')[0]
    assert cargo['last_known_location_id'] == r'\N'
    assert cargo['next_expected_location_id'] == r'\N'
    assert cargo['next_expected_voyage_id'] == r'\N'
    assert cargo['calculated_at'] == '2026-11-07T10:11:12Z'

    handling_event = _read_csv(output / 'HandlingEvent.csv')[0]
    assert handling_event['completionTime'] == '2026-11-07T08:12:13Z'
    assert handling_event['registration'] == '2026-11-07T10:13:14Z'

    leg = _read_csv(output / 'leg.csv')[0]
    assert leg['load_time'] == '2026-11-08T08:00:00Z'
    assert leg['unload_time'] == '2026-11-09T11:00:00Z'

    carrier_movement = _read_csv(output / 'carrier_movement.csv')[0]
    assert carrier_movement['arrival_time'] == '2026-11-09T10:00:00Z'
    assert carrier_movement['departure_time'] == '2026-11-08T12:00:00Z'

    assert datetime.fromisoformat(cargo['calculated_at']) == datetime(
        2026, 11, 7, 10, 11, 12, tzinfo=UTC
    )

    blocked_directory = tmp_path / 'not-a-directory'
    blocked_directory.write_text('occupied', encoding='utf-8')
    with pytest.raises(CommandError) as error:
        call_command(
            'export_data_snapshot',
            mapping=str(MAPPING),
            out=str(blocked_directory),
        )
    assert f'{blocked_directory}: unable to create output directory:' in str(error.value)

    blocked_csv = tmp_path / 'blocked-export'
    (blocked_csv / 'location.csv').mkdir(parents=True)
    with pytest.raises(CommandError) as error:
        call_command('export_data_snapshot', mapping=str(MAPPING), out=str(blocked_csv))
    assert f'{blocked_csv}/location.csv: unable to write export:' in str(error.value)
