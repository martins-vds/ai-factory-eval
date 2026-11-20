import csv
from pathlib import Path

import pytest
import yaml
from django.core.management import call_command

from cargotracker.location.infrastructure.models import LocationRecord

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING_PATH = ROOT / '.migration' / 'data' / 'mapping.yaml'
MAPPING = yaml.safe_load(MAPPING_PATH.read_text(encoding='utf-8'))


def _read_csv(path):
    with path.open(newline='', encoding='utf-8') as stream:
        return list(csv.reader(stream))


def _load_fixture():
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(MAPPING_PATH),
    )


@pytest.mark.django_db(transaction=True)
def test_export_snapshot_round_trips_fixture_rows(tmp_path):
    _load_fixture()
    output = tmp_path / 'target-export'

    call_command('export_data_snapshot', mapping=str(MAPPING_PATH), out=str(output))

    assert {path.stem for path in output.glob('*.csv')} == {
        spec['target'] for spec in MAPPING['tables']
    }
    exported = {}
    for spec in MAPPING['tables']:
        data = _read_csv(output / f"{spec['target']}.csv")
        source_data = _read_csv(FIXTURE_SNAPSHOT / f"{spec['source']}.csv")
        assert data[0] == list(spec['columns'])
        assert len(data) - 1 == len(source_data) - 1
        exported[spec['target']] = data

    assert exported['location'][1:] == [
        ['101', 'USNYC', 'New York'],
        ['102', 'NLRTM', 'Rotterdam'],
    ]
    assert exported['voyage'][1:] == [['900', '']]
    cargo_header, cargo_row = exported['cargo'][0], exported['cargo'][1]
    assert cargo_row[cargo_header.index('last_known_location_id')] == r'\N'
    assert cargo_row[cargo_header.index('eta')] == r'\N'
    assert cargo_row[cargo_header.index('calculated_at')] == '2026-11-07T10:11:12Z'
    event_header, event_row = exported['HandlingEvent'][0], exported['HandlingEvent'][1]
    assert event_row[event_header.index('completionTime')] == '2026-11-07T08:12:13Z'
    leg_header, leg_row = exported['leg'][0], exported['leg'][1]
    assert leg_row[leg_header.index('load_time')] == '2026-11-08T08:00:00Z'
    movement_header, movement_row = exported['carrier_movement'][0], exported['carrier_movement'][1]
    assert movement_row[movement_header.index('arrival_time')] == '2026-11-09T10:00:00Z'


@pytest.mark.django_db(transaction=True)
def test_export_snapshot_orders_rows_by_primary_key(tmp_path):
    _load_fixture()
    LocationRecord.objects.create(id=100, unlocode='AUSYD', name='Sydney')
    output = tmp_path / 'target-export'

    call_command('export_data_snapshot', mapping=str(MAPPING_PATH), out=str(output))

    assert [row[0] for row in _read_csv(output / 'location.csv')[1:]] == [
        '100',
        '101',
        '102',
    ]
