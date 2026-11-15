import csv
from pathlib import Path

import pytest
import yaml
from django.core.management import call_command

from cargotracker.location.infrastructure.models import LocationRecord

ROOT = Path(__file__).resolve().parents[2]
MAPPING = ROOT / '.migration' / 'data' / 'mapping.yaml'
SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'


@pytest.mark.django_db(transaction=True)
def test_export_data_snapshot_round_trips_mapped_fixture_rows(tmp_path):
    call_command('load_data_snapshot', snapshot=str(SNAPSHOT), mapping=str(MAPPING))
    LocationRecord.objects.create(id=104, unlocode='TST04', name='Fourth')
    LocationRecord.objects.create(id=103, unlocode='TST03', name='Third')

    output = tmp_path / 'export'
    call_command('export_data_snapshot', mapping=str(MAPPING), out=str(output))

    mapping = yaml.safe_load(MAPPING.read_text(encoding='utf-8'))
    exported = {}
    for spec in mapping['tables']:
        with (output / f"{spec['target']}.csv").open(
            newline='', encoding='utf-8'
        ) as stream:
            reader = csv.DictReader(stream)
            assert reader.fieldnames == list(spec['columns'])
            rows = list(reader)
        with (SNAPSHOT / f"{spec['source']}.csv").open(
            newline='', encoding='utf-8'
        ) as stream:
            source_row_count = sum(1 for _ in csv.reader(stream)) - 1
        expected_count = source_row_count + (2 if spec['target'] == 'location' else 0)
        assert len(rows) == expected_count
        exported[spec['target']] = rows

    assert [int(row['id']) for row in exported['location']] == [101, 102, 103, 104]
    assert exported['voyage'][0]['voyage_number'] == ''
    cargo = exported['cargo'][0]
    assert cargo['last_known_location_id'] == r'\N'
    assert cargo['next_expected_location_id'] == r'\N'
    assert cargo['calculated_at'] == '2026-11-07T10:11:12+00:00'
