import csv
from pathlib import Path

import pytest
import yaml
from django.core.management import call_command
from django.core.management.base import CommandError

from cargotracker.location.infrastructure.models import LocationRecord

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = PROJECT_ROOT / '.migration' / 'data' / 'mapping.yaml'


@pytest.mark.django_db(transaction=True)
def test_export_data_snapshot_round_trips_mapped_fixture_rows(tmp_path):
    mapping = yaml.safe_load(MAPPING.read_text(encoding='utf-8'))
    call_command(
        'load_data_snapshot',
        snapshot=str(FIXTURE_SNAPSHOT),
        mapping=str(MAPPING),
    )

    output = tmp_path / 'export'
    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(output))

    assert {path.name for path in output.glob('*.csv')} == {
        f'{spec["target"]}.csv' for spec in mapping['tables']
    }
    for spec in mapping['tables']:
        with (output / f'{spec["target"]}.csv').open(newline='', encoding='utf-8') as csv_file:
            rows = list(csv.DictReader(csv_file))
        with (FIXTURE_SNAPSHOT / f'{spec["source"]}.csv').open(
            newline='', encoding='utf-8'
        ) as csv_file:
            source_rows = list(csv.DictReader(csv_file))

        assert len(rows) == len(source_rows)
        assert list(rows[0]) == list(spec['columns'])
        assert [int(row['id']) for row in rows] == sorted(int(row['id']) for row in rows)

    with (output / 'cargo.csv').open(newline='', encoding='utf-8') as csv_file:
        cargo = list(csv.DictReader(csv_file))
    assert cargo[0]['last_known_location_id'] == r'\N'
    assert cargo[0]['calculated_at'] == '2026-11-07T10:11:12Z'

    with (output / 'voyage.csv').open(newline='', encoding='utf-8') as csv_file:
        voyage = list(csv.DictReader(csv_file))
    assert voyage[0]['voyage_number'] == ''


@pytest.mark.django_db
def test_export_rejects_literal_null_marker_values(tmp_path):
    LocationRecord.objects.create(id=1, unlocode='USNYC', name=r'\N')
    mapping = tmp_path / 'mapping.yaml'
    mapping.write_text(
        yaml.safe_dump(
            {
                'tables': [
                    {
                        'target': 'location',
                        'columns': {'id': 'id', 'unlocode': 'unlocode', 'name': 'name'},
                    }
                ]
            }
        ),
        encoding='utf-8',
    )

    with pytest.raises(CommandError, match='literal value'):
        call_command(
            'export_data_snapshot',
            mapping=str(mapping),
            out=str(tmp_path / 'export'),
        )
