import csv
import subprocess
import sys
from pathlib import Path

import pytest
from django.core.management import call_command

from cargotracker.location.infrastructure.models import LocationRecord

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = REPOSITORY_ROOT / '.migration' / 'data' / 'mapping.yaml'
RECONCILER = REPOSITORY_ROOT / '.migration' / 'harness' / 'tools' / 'data_reconcile.py'


@pytest.mark.django_db(transaction=True)
def test_export_data_snapshot_round_trips_fixture_rows_and_preserves_nulls(tmp_path):
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(MAPPING),
    )
    output = tmp_path / 'export'

    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(output))

    assert {path.name for path in output.glob('*.csv')} == {
        'location.csv',
        'voyage.csv',
        'cargo.csv',
        'HandlingEvent.csv',
        'leg.csv',
        'carrier_movement.csv',
    }

    result = subprocess.run(
        [
            sys.executable,
            str(RECONCILER),
            'reconcile',
            '--snapshot',
            str(FIXTURE_SNAPSHOT),
            '--target',
            str(output),
            '--mapping',
            str(MAPPING),
        ],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f'{result.stdout}\n{result.stderr}'

    with (output / 'cargo.csv').open(newline='', encoding='utf-8') as stream:
        cargo = next(csv.DictReader(stream))
    with (output / 'voyage.csv').open(newline='', encoding='utf-8') as stream:
        voyage = next(csv.DictReader(stream))

    assert cargo['last_known_location_id'] == '\\N'
    assert cargo['calculated_at'] == '2026-11-07T10:11:12Z'
    assert voyage['voyage_number'] == ''


@pytest.mark.django_db(transaction=True)
def test_export_data_snapshot_orders_rows_by_primary_key(tmp_path):
    LocationRecord.objects.create(id=20, unlocode='TST20', name='Later')
    LocationRecord.objects.create(id=10, unlocode='TST10', name='Earlier')

    output = tmp_path / 'export'
    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(output))

    with (output / 'location.csv').open(newline='', encoding='utf-8') as stream:
        locations = list(csv.DictReader(stream))

    assert [row['id'] for row in locations] == ['10', '20']
