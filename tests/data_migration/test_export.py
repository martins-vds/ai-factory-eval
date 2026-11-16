import csv
import re
import subprocess
import sys
from io import StringIO
from pathlib import Path

import pytest
import yaml
from django.core.management import call_command
from django.core.management.base import CommandError

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
    target = tmp_path / 'nested' / 'target'
    output = StringIO()
    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(target), stdout=output)
    assert 'Exported 7 rows across 6 mapped tables.' in output.getvalue()
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


@pytest.mark.django_db
def test_export_rejects_invalid_mappings(tmp_path):
    mapping_file = tmp_path / 'mapping.yaml'
    invalid_mappings = [
        ([], 'mapping must be an object'),
        ({'tables': []}, 'mapping has no tables'),
        ({'tables': [None]}, 'each mapped table must be an object'),
        (
            {'tables': [{'target': None, 'columns': {'id': 'id'}}]},
            'mapping targets must be unique table names',
        ),
        (
            {'tables': [{'target': 'missing', 'columns': {'id': 'id'}}]},
            'missing: no registered Django model for target table',
        ),
        (
            {'tables': [{'target': 'location', 'columns': ['id']}]},
            'location: mapping has no columns',
        ),
        (
            {'tables': [{'target': 'location', 'columns': {'unknown': 'unknown'}}]},
            'no target column',
        ),
        ({'tables': [{'target': 'location', 'columns': {}}]}, 'location: mapping has no columns'),
        (
            {'tables': [{'target': 'location', 'columns': {'name': 'name'}}]},
            'location: mapping must include its primary key',
        ),
        (
            {
                'tables': [
                    {'target': 'location', 'columns': {'id': 'id'}},
                    {'target': 'location', 'columns': {'id': 'id'}},
                ]
            },
            'mapping targets must be unique table names',
        ),
    ]

    for mapping, message in invalid_mappings:
        mapping_file.write_text(yaml.safe_dump(mapping), encoding='utf-8')
        with pytest.raises(CommandError, match=re.escape(message)):
            call_command(
                'export_data_snapshot',
                mapping=str(mapping_file),
                out=str(tmp_path / 'target'),
            )

    with pytest.raises(CommandError, match='unable to read mapping'):
        call_command(
            'export_data_snapshot',
            mapping=str(tmp_path / 'missing.yaml'),
            out=str(tmp_path / 'target'),
        )


@pytest.mark.django_db
def test_export_requires_both_arguments():
    with pytest.raises(CommandError, match='--mapping'):
        call_command('export_data_snapshot', out='target')
    with pytest.raises(CommandError, match='--out'):
        call_command('export_data_snapshot', mapping=str(MAPPING))


@pytest.mark.django_db
def test_export_reports_output_path_errors(tmp_path):
    mapping_file = tmp_path / 'mapping.yaml'
    mapping_file.write_text(
        yaml.safe_dump({'tables': [{'target': 'location', 'columns': {'id': 'id'}}]}),
        encoding='utf-8',
    )
    output_file = tmp_path / 'not-a-directory'
    output_file.write_text('occupied', encoding='utf-8')
    with pytest.raises(CommandError, match=re.escape(str(output_file))):
        call_command(
            'export_data_snapshot',
            mapping=str(mapping_file),
            out=str(output_file),
        )

    output_dir = tmp_path / 'target'
    output_dir.mkdir()
    (output_dir / 'location.csv').mkdir()
    with pytest.raises(CommandError, match=re.escape(str(output_dir / 'location.csv'))):
        call_command(
            'export_data_snapshot',
            mapping=str(mapping_file),
            out=str(output_dir),
        )
