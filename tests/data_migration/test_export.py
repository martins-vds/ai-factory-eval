import csv
import subprocess
import sys
from pathlib import Path

import pytest
from django.core.management import call_command

ROOT = Path(__file__).parents[2]
FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = ROOT / '.migration' / 'data' / 'mapping.yaml'


@pytest.mark.django_db(transaction=True)
def test_export_data_snapshot_round_trips_fixture_rows(tmp_path):
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(MAPPING),
    )
    output = tmp_path / 'target-export'

    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(output))

    assert {path.name for path in output.glob('*.csv')} == {
        'location.csv',
        'voyage.csv',
        'cargo.csv',
        'HandlingEvent.csv',
        'leg.csv',
        'carrier_movement.csv',
    }

    with (output / 'voyage.csv').open(newline='', encoding='utf-8') as stream:
        voyages = list(csv.DictReader(stream))
    assert voyages == [{'id': '900', 'voyage_number': ''}]

    with (output / 'cargo.csv').open(newline='', encoding='utf-8') as stream:
        cargo = list(csv.DictReader(stream))
    assert cargo[0]['eta'] == '2026-12-29'
    assert cargo[0]['last_known_location_id'] == r'\N'
    assert cargo[0]['calculated_at'] == '2026-11-07T10:11:12Z'
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
            '--report',
            str(tmp_path / 'reconciliation.md'),
        ],
        capture_output=True,
        check=False,
        cwd=ROOT,
        text=True,
    )
    assert reconciliation.returncode == 0, reconciliation.stdout + reconciliation.stderr


@pytest.mark.django_db
def test_export_data_snapshot_orders_rows_by_primary_key(tmp_path):
    from cargotracker.location.infrastructure.models import LocationRecord

    LocationRecord.objects.create(id=200, unlocode='ZZZZZ', name='Later')
    LocationRecord.objects.create(id=100, unlocode='AAAAA', name='Earlier')
    mapping = tmp_path / 'mapping.yaml'
    mapping.write_text(
        'tables:\n'
        '  - target: location\n'
        '    key: [id]\n'
        '    columns:\n'
        '      id: id\n'
        '      unlocode: unlocode\n'
        '      name: name\n',
        encoding='utf-8',
    )
    output = tmp_path / 'target-export'

    call_command('export_data_snapshot', mapping=str(mapping), out=str(output))

    with (output / 'location.csv').open(newline='', encoding='utf-8') as stream:
        rows = list(csv.DictReader(stream))
    assert [row['id'] for row in rows] == ['100', '200']
