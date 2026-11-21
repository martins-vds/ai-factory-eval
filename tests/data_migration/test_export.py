import csv
import subprocess
import sys
from pathlib import Path

import pytest
from django.core.management import call_command

from cargotracker.location.infrastructure.models import LocationRecord

REPOSITORY_ROOT = Path(__file__).parents[2]
FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = REPOSITORY_ROOT / '.migration' / 'data' / 'mapping.yaml'


@pytest.mark.django_db(transaction=True)
def test_export_snapshot_round_trips_fixture_and_preserves_null_and_empty(tmp_path):
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(MAPPING),
    )
    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(tmp_path))

    report = tmp_path / 'reconciliation.md'
    result = subprocess.run(
        [
            sys.executable,
            '.migration/harness/tools/data_reconcile.py',
            'reconcile',
            '--snapshot',
            str(FIXTURE_SNAPSHOT),
            '--target',
            str(tmp_path),
            '--mapping',
            str(MAPPING),
            '--report',
            str(report),
        ],
        capture_output=True,
        check=False,
        cwd=REPOSITORY_ROOT,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    with (tmp_path / 'cargo.csv').open(newline='', encoding='utf-8') as stream:
        cargo = next(csv.DictReader(stream))
    with (tmp_path / 'voyage.csv').open(newline='', encoding='utf-8') as stream:
        voyage = next(csv.DictReader(stream))

    assert cargo['last_known_location_id'] == r'\N'
    assert voyage['voyage_number'] == ''


@pytest.mark.django_db(transaction=True)
def test_export_snapshot_orders_rows_by_primary_key(tmp_path):
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(MAPPING),
    )
    LocationRecord.objects.create(id=100, unlocode='TST00', name='Test')
    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(tmp_path))

    with (tmp_path / 'location.csv').open(newline='', encoding='utf-8') as stream:
        ids = [row['id'] for row in csv.DictReader(stream)]

    assert ids == ['100', '101', '102']
