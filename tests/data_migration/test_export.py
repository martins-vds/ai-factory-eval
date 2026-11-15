import subprocess
import sys
from pathlib import Path

import pytest
from django.core.management import call_command

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
