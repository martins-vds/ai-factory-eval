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


def _load_fixture():
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(MAPPING),
    )


def _export_fixture(output):
    call_command(
        'export_data_snapshot',
        mapping=str(MAPPING),
        out=str(output),
    )


def _records(path):
    with path.open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))


@pytest.mark.django_db(transaction=True)
def test_export_snapshot_round_trips_fixture_rows_and_preserves_null_and_empty(tmp_path):
    _load_fixture()
    output = tmp_path / 'export'

    _export_fixture(output)

    assert {
        'location.csv',
        'voyage.csv',
        'cargo.csv',
        'HandlingEvent.csv',
        'leg.csv',
        'carrier_movement.csv',
    } == {path.name for path in output.glob('*.csv')}

    result = subprocess.run(
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
        capture_output=True,
        check=True,
        text=True,
    )
    assert 'AFS-RESULT gate=data-reconcile' in result.stdout

    assert _records(output / 'cargo.csv')[0]['last_known_location_id'] == r'\N'
    assert _records(output / 'voyage.csv')[0]['voyage_number'] == ''
    assert _records(output / 'cargo.csv')[0]['calculated_at'] == '2026-11-07T10:11:12Z'


@pytest.mark.django_db(transaction=True)
def test_export_snapshot_orders_rows_by_primary_key(tmp_path):
    _load_fixture()
    LocationRecord.objects.create(id=104, unlocode='TST04', name='Fourth')
    LocationRecord.objects.create(id=103, unlocode='TST03', name='Third')
    output = tmp_path / 'export'

    _export_fixture(output)

    assert [row['id'] for row in _records(output / 'location.csv')] == [
        '101',
        '102',
        '103',
        '104',
    ]
