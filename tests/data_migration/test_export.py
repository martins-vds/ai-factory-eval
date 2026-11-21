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


def _export_fixture(output):
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(MAPPING),
    )
    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(output))


@pytest.mark.django_db(transaction=True)
def test_export_round_trips_fixture_snapshot(tmp_path):
    output = tmp_path / 'export'
    _export_fixture(output)

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
        check=False,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert 'mismatched_tables=0' in result.stdout


@pytest.mark.django_db(transaction=True)
def test_export_orders_rows_by_primary_key(tmp_path):
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(MAPPING),
    )
    LocationRecord.objects.create(pk=204, unlocode='ZZZ02', name='Second')
    LocationRecord.objects.create(pk=203, unlocode='ZZZ01', name='First')
    output = tmp_path / 'export'
    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(output))

    with (output / 'location.csv').open(newline='', encoding='utf-8') as stream:
        ids = [int(row['id']) for row in csv.DictReader(stream)]

    assert ids == [101, 102, 203, 204]


@pytest.mark.django_db(transaction=True)
def test_export_preserves_null_empty_string_and_utc_timestamps(tmp_path):
    output = tmp_path / 'export'
    _export_fixture(output)

    with (output / 'cargo.csv').open(newline='', encoding='utf-8') as stream:
        cargo = next(csv.DictReader(stream))
    with (output / 'voyage.csv').open(newline='', encoding='utf-8') as stream:
        voyage = next(csv.DictReader(stream))

    assert cargo['last_known_location_id'] == r'\N'
    assert voyage['voyage_number'] == ''
    assert cargo['calculated_at'] == '2026-11-07T10:11:12Z'
