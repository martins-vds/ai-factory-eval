import csv
import subprocess
import sys
from pathlib import Path

import pytest
from django.core.management import call_command

from cargotracker.location.infrastructure.models import LocationRecord

FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = Path(__file__).parents[2] / '.migration' / 'data' / 'mapping.yaml'
RECONCILE = Path(__file__).parents[2] / '.migration' / 'harness' / 'tools' / 'data_reconcile.py'


@pytest.mark.django_db(transaction=True)
def test_export_round_trips_snapshot_fixture(tmp_path):
    call_command('load_data_snapshot', snapshot=str(FIXTURE_SNAPSHOT), mapping=str(MAPPING))
    exported = tmp_path / 'target'

    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(exported))

    result = subprocess.run(
        [
            sys.executable,
            str(RECONCILE),
            'reconcile',
            '--snapshot',
            str(FIXTURE_SNAPSHOT),
            '--target',
            str(exported),
            '--mapping',
            str(MAPPING),
        ],
        capture_output=True,
        check=False,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.django_db(transaction=True)
def test_export_distinguishes_null_from_empty_string(tmp_path):
    call_command('load_data_snapshot', snapshot=str(FIXTURE_SNAPSHOT), mapping=str(MAPPING))
    LocationRecord.objects.filter(pk=101).update(name='')
    exported = tmp_path / 'target'

    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(exported))

    with (exported / 'cargo.csv').open(encoding='utf-8', newline='') as stream:
        cargo = next(csv.DictReader(stream))
    with (exported / 'location.csv').open(encoding='utf-8', newline='') as stream:
        location = next(csv.DictReader(stream))
    assert cargo['last_known_location_id'] == '\\N'
    assert location['name'] == ''


@pytest.mark.django_db(transaction=True)
def test_export_orders_by_primary_key_and_writes_utc_timestamps(tmp_path):
    call_command('load_data_snapshot', snapshot=str(FIXTURE_SNAPSHOT), mapping=str(MAPPING))
    LocationRecord.objects.create(pk=104, unlocode='ZZZZZ', name='Z')
    LocationRecord.objects.create(pk=103, unlocode='YYYYY', name='Y')
    exported = tmp_path / 'target'

    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(exported))

    with (exported / 'location.csv').open(encoding='utf-8', newline='') as stream:
        locations = list(csv.DictReader(stream))
    with (exported / 'HandlingEvent.csv').open(encoding='utf-8', newline='') as stream:
        event = next(csv.DictReader(stream))
    with (exported / 'cargo.csv').open(encoding='utf-8', newline='') as stream:
        cargo = next(csv.DictReader(stream))
    assert [int(row['id']) for row in locations] == [101, 102, 103, 104]
    assert event['completionTime'] == '2026-11-07T08:12:13Z'
    assert event['registration'] == '2026-11-07T10:13:14Z'
    assert cargo['calculated_at'] == '2026-11-07T10:11:12Z'
