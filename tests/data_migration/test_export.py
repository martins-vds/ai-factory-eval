import csv
from pathlib import Path

import pytest
import yaml
from django.core.management import call_command


ROOT = Path(__file__).parents[2]
FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = ROOT / '.migration' / 'data' / 'mapping.yaml'


@pytest.mark.django_db(transaction=True)
def test_export_snapshot_round_trips_fixture_and_preserves_nulls(tmp_path):
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(MAPPING),
    )
    output = tmp_path / 'export'

    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(output))

    mapping = yaml.safe_load(MAPPING.read_text(encoding='utf-8'))
    assert {path.stem for path in output.glob('*.csv')} == {
        table['target'] for table in mapping['tables']
    }

    with (output / 'location.csv').open(newline='', encoding='utf-8') as stream:
        locations = list(csv.DictReader(stream))
    assert locations == [
        {'id': '101', 'unlocode': 'USNYC', 'name': 'New York'},
        {'id': '102', 'unlocode': 'NLRTM', 'name': 'Rotterdam'},
    ]

    with (output / 'voyage.csv').open(newline='', encoding='utf-8') as stream:
        voyages = list(csv.DictReader(stream))
    assert voyages == [{'id': '900', 'voyage_number': ''}]

    with (output / 'cargo.csv').open(newline='', encoding='utf-8') as stream:
        cargo = list(csv.DictReader(stream))
    assert cargo[0]['last_known_location_id'] == r'\N'
    assert cargo[0]['calculated_at'] == '2026-11-07T10:11:12+00:00'
    assert '""' in (output / 'voyage.csv').read_text(encoding='utf-8')
    assert r'"\N"' in (output / 'cargo.csv').read_text(encoding='utf-8')
