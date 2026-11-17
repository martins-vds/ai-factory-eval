import csv
import hashlib
import json
import shutil
from pathlib import Path

import pytest
import yaml
from django.core.management import call_command

FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING_PATH = Path(__file__).parents[2] / '.migration' / 'data' / 'mapping.yaml'


def _reverse_location_rows(snapshot):
    source = snapshot / 'LOCATION.csv'
    with source.open(newline='', encoding='utf-8') as stream:
        rows = list(csv.reader(stream))
    with source.open('w', newline='', encoding='utf-8') as stream:
        csv.writer(stream).writerows([rows[0], *reversed(rows[1:])])

    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest['tables']['LOCATION']['sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')


@pytest.mark.django_db(transaction=True)
def test_export_snapshot_round_trips_fixture_rows(tmp_path):
    snapshot = tmp_path / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)
    _reverse_location_rows(snapshot)

    call_command('load_data_snapshot', snapshot=str(snapshot), mapping=str(MAPPING_PATH))
    output = tmp_path / 'target'
    call_command('export_data_snapshot', mapping=str(MAPPING_PATH), out=str(output))

    mapping = yaml.safe_load(MAPPING_PATH.read_text(encoding='utf-8'))
    assert {path.stem for path in output.glob('*.csv')} == {
        table['target'] for table in mapping['tables']
    }

    location_rows = list(csv.DictReader((output / 'location.csv').open(newline='', encoding='utf-8')))
    assert [row['id'] for row in location_rows] == ['101', '102']

    cargo_rows = list(csv.DictReader((output / 'cargo.csv').open(newline='', encoding='utf-8')))
    assert cargo_rows[0]['last_known_location_id'] == r'\N'
    voyage_rows = list(csv.DictReader((output / 'voyage.csv').open(newline='', encoding='utf-8')))
    assert voyage_rows[0]['voyage_number'] == ''

    leg_rows = list(csv.DictReader((output / 'leg.csv').open(newline='', encoding='utf-8')))
    assert leg_rows[0]['load_time'] == '2026-11-08T08:00:00+00:00'

    result = __import__('subprocess').run(
        [
            'python',
            '.migration/harness/tools/data_reconcile.py',
            'reconcile',
            '--snapshot',
            str(snapshot),
            '--target',
            str(output),
            '--mapping',
            str(MAPPING_PATH),
        ],
        capture_output=True,
        text=True,
        check=False,
        cwd=Path(__file__).parents[2],
    )
    assert result.returncode == 0, result.stdout + result.stderr
