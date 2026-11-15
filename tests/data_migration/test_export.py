import csv
import subprocess
import sys
from pathlib import Path

import pytest
from django.core.management import call_command

from cargotracker.location.infrastructure.models import LocationRecord


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = ROOT / '.migration' / 'data' / 'mapping.yaml'


def _read_rows(path):
    with path.open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))


@pytest.mark.django_db(transaction=True)
def test_export_data_snapshot_round_trips_fixture_rows(tmp_path):
    output = tmp_path / 'target'
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(MAPPING),
    )
    call_command(
        'export_data_snapshot',
        mapping=str(MAPPING),
        out=str(output),
    )

    tables = {
        'carrier_movement',
        'cargo',
        'HandlingEvent',
        'leg',
        'location',
        'voyage',
    }
    assert {path.stem for path in output.glob('*.csv')} == tables

    for table in tables:
        rows = _read_rows(output / f'{table}.csv')
        assert [int(row['id']) for row in rows] == sorted(
            int(row['id']) for row in rows
        )

    cargo = _read_rows(output / 'cargo.csv')[0]
    voyage = _read_rows(output / 'voyage.csv')[0]
    assert cargo['last_known_location_id'] == r'\N'
    assert voyage['voyage_number'] == ''
    assert cargo['calculated_at'] == '2026-11-07T10:11:12Z'
    assert (output / 'cargo.csv').read_text(encoding='utf-8').count(r'"\N"') > 0
    assert '""' in (output / 'voyage.csv').read_text(encoding='utf-8')

    reconciliation = subprocess.run(
        [
            sys.executable,
            str(ROOT / '.migration' / 'harness' / 'tools' / 'data_reconcile.py'),
            'reconcile',
            '--snapshot',
            str(FIXTURE_SNAPSHOT),
            '--target',
            str(output),
            '--mapping',
            str(MAPPING),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert reconciliation.returncode == 0, reconciliation.stdout + reconciliation.stderr


@pytest.mark.django_db
def test_export_data_snapshot_orders_rows_by_primary_key(tmp_path):
    LocationRecord.objects.create(id=102, unlocode='ZZZ', name='Later')
    LocationRecord.objects.create(id=101, unlocode='AAA', name='Earlier')
    output = tmp_path / 'target'

    call_command(
        'export_data_snapshot',
        mapping=str(MAPPING),
        out=str(output),
    )

    assert [row['id'] for row in _read_rows(output / 'location.csv')] == ['101', '102']
