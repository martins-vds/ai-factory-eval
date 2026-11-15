import csv
import subprocess
import sys
from pathlib import Path

import pytest
from django.core.management import call_command

from cargotracker.location.infrastructure.models import LocationRecord

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING_FILE = ROOT / '.migration' / 'data' / 'mapping.yaml'
RECONCILE_TOOL = ROOT / '.migration' / 'harness' / 'tools' / 'data_reconcile.py'


@pytest.mark.django_db(transaction=True)
def test_export_data_snapshot_round_trips_fixture_rows_and_preserves_nulls(tmp_path):
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(MAPPING_FILE),
    )
    export_dir = tmp_path / 'export'

    call_command('export_data_snapshot', mapping=str(MAPPING_FILE), out=str(export_dir))

    assert {path.stem for path in export_dir.glob('*.csv')} == {
        'location',
        'voyage',
        'cargo',
        'HandlingEvent',
        'leg',
        'carrier_movement',
    }

    with (export_dir / 'cargo.csv').open(newline='', encoding='utf-8') as stream:
        cargo = next(csv.DictReader(stream))
    with (export_dir / 'voyage.csv').open(newline='', encoding='utf-8') as stream:
        voyage = next(csv.DictReader(stream))

    assert cargo['last_known_location_id'] == '\\N'
    assert voyage['voyage_number'] == ''
    assert '""' in (export_dir / 'voyage.csv').read_text(encoding='utf-8')

    result = subprocess.run(
        [
            sys.executable,
            str(RECONCILE_TOOL),
            'reconcile',
            '--snapshot',
            str(FIXTURE_SNAPSHOT),
            '--target',
            str(export_dir),
            '--mapping',
            str(MAPPING_FILE),
            '--report',
            str(tmp_path / 'reconciliation.md'),
        ],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.django_db(transaction=True)
def test_export_data_snapshot_orders_rows_by_primary_key(tmp_path):
    LocationRecord.objects.create(id=20, unlocode='TST20', name='Later')
    LocationRecord.objects.create(id=10, unlocode='TST10', name='Earlier')

    export_dir = tmp_path / 'export'
    call_command('export_data_snapshot', mapping=str(MAPPING_FILE), out=str(export_dir))

    with (export_dir / 'location.csv').open(newline='', encoding='utf-8') as stream:
        ids = [row['id'] for row in csv.DictReader(stream)]

    assert ids == ['10', '20']
