import csv
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from django.core.management import call_command

from cargotracker.voyage.infrastructure.models import VoyageRecord

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = ROOT / '.migration' / 'data' / 'mapping.yaml'


def _export_fixture(tmp_path):
    output = tmp_path / 'export'
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(MAPPING),
    )
    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(output))
    return output


@pytest.mark.django_db(transaction=True)
def test_export_snapshot_round_trips_fixture_rows(tmp_path):
    output = _export_fixture(tmp_path)
    mapping = yaml.safe_load(MAPPING.read_text(encoding='utf-8'))
    assert {path.name for path in output.glob('*.csv')} == {
        f'{table["target"]}.csv' for table in mapping['tables']
    }

    report = tmp_path / 'reconciliation.md'
    result = subprocess.run(
        [
            sys.executable,
            '.migration/harness/tools/data_reconcile.py',
            'reconcile',
            '--snapshot',
            str(FIXTURE_SNAPSHOT),
            '--target',
            str(output),
            '--mapping',
            str(MAPPING),
            '--report',
            str(report),
        ],
        cwd=ROOT,
        capture_output=True,
        check=True,
        text=True,
    )
    assert 'AFS-RESULT gate=data-reconcile tables=6 rows=7 mismatched_tables=0' in result.stdout


@pytest.mark.django_db(transaction=True)
def test_export_snapshot_preserves_null_empty_string_and_utc_timestamp(tmp_path):
    output = _export_fixture(tmp_path)

    with (output / 'cargo.csv').open(newline='', encoding='utf-8') as stream:
        cargo = next(csv.DictReader(stream))
    with (output / 'voyage.csv').open(newline='', encoding='utf-8') as stream:
        voyage = next(csv.DictReader(stream))

    assert cargo['last_known_location_id'] == r'\N'
    assert voyage['voyage_number'] == ''
    assert cargo['calculated_at'] == '2026-11-07T10:11:12Z'


@pytest.mark.django_db(transaction=True)
def test_export_snapshot_orders_rows_by_primary_key(tmp_path):
    VoyageRecord.objects.create(id=20, voyage_number='V020')
    VoyageRecord.objects.create(id=10, voyage_number='V010')
    mapping = yaml.safe_load(MAPPING.read_text(encoding='utf-8'))
    mapping['tables'] = [mapping['tables'][1]]
    mapping_path = tmp_path / 'mapping.yaml'
    mapping_path.write_text(yaml.safe_dump(mapping), encoding='utf-8')
    output = tmp_path / 'export'

    call_command('export_data_snapshot', mapping=str(mapping_path), out=str(output))

    with (output / 'voyage.csv').open(newline='', encoding='utf-8') as stream:
        rows = list(csv.DictReader(stream))
    assert [row['id'] for row in rows] == ['10', '20']
