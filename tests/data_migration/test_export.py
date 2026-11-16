import csv
import subprocess
import sys
from pathlib import Path

import pytest
from django.core.management import call_command

from cargotracker.location.infrastructure.models import LocationRecord

ROOT = Path(__file__).parents[2]
FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = ROOT / '.migration' / 'data' / 'mapping.yaml'
RECONCILER = ROOT / '.migration' / 'harness' / 'tools' / 'data_reconcile.py'


def _read_rows(path):
    with path.open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))


@pytest.mark.django_db(transaction=True)
def test_export_data_snapshot_round_trips_fixture_and_preserves_nulls(tmp_path):
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(MAPPING),
    )
    target = tmp_path / 'target'
    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(target))

    reconciliation = subprocess.run(
        [
            sys.executable,
            str(RECONCILER),
            'reconcile',
            '--snapshot',
            str(FIXTURE_SNAPSHOT),
            '--target',
            str(target),
            '--mapping',
            str(MAPPING),
        ],
        capture_output=True,
        check=False,
        text=True,
    )
    assert reconciliation.returncode == 0, reconciliation.stdout + reconciliation.stderr

    cargo = _read_rows(target / 'cargo.csv')[0]
    voyage = _read_rows(target / 'voyage.csv')[0]
    handling_event = _read_rows(target / 'HandlingEvent.csv')[0]
    assert cargo['last_known_location_id'] == r'\N'
    assert voyage['voyage_number'] == ''
    assert handling_event['completionTime'] == '2026-11-07T08:12:13Z'

    LocationRecord.objects.create(id=100, unlocode='AAA00', name='Earlier')
    ordered_target = tmp_path / 'ordered-target'
    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(ordered_target))
    assert [row['id'] for row in _read_rows(ordered_target / 'location.csv')] == [
        '100',
        '101',
        '102',
    ]
