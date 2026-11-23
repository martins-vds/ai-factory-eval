import csv
import subprocess
import sys
from pathlib import Path

import pytest
from django.core.management import call_command

from cargotracker.location.infrastructure.models import LocationRecord

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_SNAPSHOT = PROJECT_ROOT / 'tests/data_migration/fixtures/DM-05C'
MAPPING = PROJECT_ROOT / '.migration/data/mapping.yaml'
RECONCILE = PROJECT_ROOT / '.migration/harness/tools/data_reconcile.py'


def _export_fixture(out):
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(MAPPING),
    )
    call_command(
        'export_data_snapshot',
        mapping=str(MAPPING),
        out=str(out),
    )


@pytest.mark.django_db(transaction=True)
def test_export_round_trips_fixture_and_preserves_null_and_empty_string(tmp_path):
    out = tmp_path / 'target'
    _export_fixture(out)

    reconciliation = subprocess.run(
        [
            sys.executable,
            str(RECONCILE),
            'reconcile',
            '--snapshot',
            str(FIXTURE_SNAPSHOT),
            '--target',
            str(out),
            '--mapping',
            str(MAPPING),
        ],
        capture_output=True,
        check=False,
        cwd=PROJECT_ROOT,
        text=True,
    )
    assert reconciliation.returncode == 0, reconciliation.stdout + reconciliation.stderr

    with (out / 'voyage.csv').open(newline='', encoding='utf-8') as stream:
        voyage = list(csv.DictReader(stream))
    assert voyage == [{'id': '900', 'voyage_number': ''}]

    with (out / 'cargo.csv').open(newline='', encoding='utf-8') as stream:
        cargo = next(csv.DictReader(stream))
    assert cargo['last_known_location_id'] == r'\N'
    assert cargo['eta'] == r'\N'
    assert cargo['calculated_at'] == '2026-11-07T10:11:12Z'


@pytest.mark.django_db(transaction=True)
def test_export_orders_rows_by_primary_key(tmp_path):
    _export_fixture(tmp_path / 'target')
    LocationRecord.objects.create(id=100, unlocode='SESTO', name='Stockholm')

    out = tmp_path / 'ordered'
    call_command(
        'export_data_snapshot',
        mapping=str(MAPPING),
        out=str(out),
    )

    with (out / 'location.csv').open(newline='', encoding='utf-8') as stream:
        ids = [row['id'] for row in csv.DictReader(stream)]
    assert ids == ['100', '101', '102']
