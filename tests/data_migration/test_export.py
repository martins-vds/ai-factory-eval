import csv
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from django.core.management import call_command

from cargotracker.handling.infrastructure.models import HandlingEventRecord

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = ROOT / '.migration' / 'data' / 'mapping.yaml'


@pytest.mark.django_db(transaction=True)
def test_export_data_snapshot_round_trips_fixture_rows(tmp_path):
    call_command('load_data_snapshot', snapshot=str(FIXTURE_SNAPSHOT), mapping=str(MAPPING))
    output = tmp_path / 'export'

    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(output))

    assert {path.name for path in output.glob('*.csv')} == {
        'HandlingEvent.csv',
        'carrier_movement.csv',
        'cargo.csv',
        'leg.csv',
        'location.csv',
        'voyage.csv',
    }
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
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.django_db(transaction=True)
def test_export_data_snapshot_preserves_null_empty_string_and_utc_order(tmp_path):
    call_command('load_data_snapshot', snapshot=str(FIXTURE_SNAPSHOT), mapping=str(MAPPING))
    offset = timezone(timedelta(hours=2))
    for event_id, event_type in ((73, ''), (72, 'RECEIVE')):
        HandlingEventRecord.objects.create(
            id=event_id,
            event_type=event_type,
            voyage_id=None,
            location_id=102,
            completion_time=datetime(2026, 11, 7, 10, 12, 13, tzinfo=offset),
            registration_time=datetime(2026, 11, 7, 10, 13, 14, tzinfo=offset),
            cargo_id=13,
        )
    output = tmp_path / 'export'

    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(output))

    with (output / 'HandlingEvent.csv').open(newline='', encoding='utf-8') as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)

    assert [row['id'] for row in rows] == ['71', '72', '73']
    empty_value = rows[-1]
    assert empty_value['type'] == ''
    assert empty_value['voyage_id'] == r'\N'
    assert empty_value['completionTime'] == '2026-11-07T08:12:13Z'
