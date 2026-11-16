import csv
import json
from pathlib import Path

import pytest
import yaml
from django.core.management import call_command

FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
ROOT = Path(__file__).parents[2]
MAPPING = ROOT / '.migration' / 'data' / 'mapping.yaml'


def _read_csv(path):
    with path.open(newline='', encoding='utf-8') as stream:
        return list(csv.reader(stream))


@pytest.mark.django_db(transaction=True)
def test_export_data_snapshot_round_trips_fixture_rows(tmp_path):
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(MAPPING),
    )
    out = tmp_path / 'target'

    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(out))

    mapping = yaml.safe_load(MAPPING.read_text(encoding='utf-8'))
    manifest = json.loads((FIXTURE_SNAPSHOT / 'manifest.json').read_text(encoding='utf-8'))
    assert {path.name for path in out.glob('*.csv')} == {
        f'{spec["target"]}.csv' for spec in mapping['tables']
    }

    for spec in mapping['tables']:
        rows = _read_csv(out / f'{spec["target"]}.csv')
        assert rows[0] == list(spec['columns'])
        assert len(rows) - 1 == manifest['tables'][spec['source']]['rows']
        primary_key = spec['key'][0]
        key_index = rows[0].index(primary_key)
        assert [int(row[key_index]) for row in rows[1:]] == sorted(
            int(row[key_index]) for row in rows[1:]
        )

    cargo = list(csv.DictReader((out / 'cargo.csv').open(newline='', encoding='utf-8')))
    assert cargo[0]['last_known_location_id'] == r'\N'
    assert cargo[0]['next_expected_location_id'] == r'\N'
    assert cargo[0]['calculated_at'] == '2026-11-07T10:11:12Z'
    voyage = list(csv.DictReader((out / 'voyage.csv').open(newline='', encoding='utf-8')))
    assert voyage[0]['voyage_number'] == ''


@pytest.mark.django_db(transaction=True)
def test_export_data_snapshot_orders_rows_by_primary_key(tmp_path):
    from cargotracker.location.infrastructure.models import LocationRecord

    LocationRecord.objects.create(id=202, unlocode='USLAX', name='Los Angeles')
    LocationRecord.objects.create(id=101, unlocode='USNYC', name='New York')
    mapping = tmp_path / 'mapping.yaml'
    mapping.write_text(
        yaml.safe_dump(
            {
                'tables': [
                    {
                        'target': 'location',
                        'columns': {'id': 'id', 'unlocode': 'unlocode', 'name': 'name'},
                    }
                ]
            }
        ),
        encoding='utf-8',
    )
    out = tmp_path / 'target'

    call_command('export_data_snapshot', mapping=str(mapping), out=str(out))

    assert _read_csv(out / 'location.csv') == [
        ['id', 'unlocode', 'name'],
        ['101', 'USNYC', 'New York'],
        ['202', 'USLAX', 'Los Angeles'],
    ]
