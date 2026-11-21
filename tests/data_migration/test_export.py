import csv
import json
from pathlib import Path

import pytest
import yaml
from django.core.management import call_command

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING_FILE = ROOT / '.migration' / 'data' / 'mapping.yaml'


@pytest.mark.django_db(transaction=True)
def test_export_data_snapshot_round_trips_fixture_rows_and_preserves_nulls(tmp_path):
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(MAPPING_FILE),
    )
    output = tmp_path / 'export'
    call_command(
        'export_data_snapshot',
        mapping=str(MAPPING_FILE),
        out=str(output),
    )

    mapping = yaml.safe_load(MAPPING_FILE.read_text(encoding='utf-8'))
    manifest = json.loads((FIXTURE_SNAPSHOT / 'manifest.json').read_text(encoding='utf-8'))
    assert {path.stem for path in output.glob('*.csv')} == {
        table['target'] for table in mapping['tables']
    }

    exported = {}
    for spec in mapping['tables']:
        with (output / f'{spec["target"]}.csv').open(newline='', encoding='utf-8') as stream:
            reader = csv.DictReader(stream)
            rows = list(reader)
        assert reader.fieldnames == list(spec['columns'])
        assert len(rows) == manifest['tables'][spec['source']]['rows']
        assert [int(row[spec['key'][0]]) for row in rows] == sorted(
            int(row[spec['key'][0]]) for row in rows
        )
        exported[spec['target']] = rows

    assert exported['location'] == [
        {'id': '101', 'unlocode': 'USNYC', 'name': 'New York'},
        {'id': '102', 'unlocode': 'NLRTM', 'name': 'Rotterdam'},
    ]
    assert exported['voyage'] == [{'id': '900', 'voyage_number': ''}]
    assert exported['cargo'][0]['last_known_location_id'] == r'\N'
    assert exported['cargo'][0]['calculated_at'] == '2026-11-07T10:11:12Z'
