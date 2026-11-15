import csv
from pathlib import Path

import pytest
import yaml
from django.core.management import call_command

from cargotracker.location.infrastructure.models import LocationRecord

SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = {
    'defaults': {'timestamp_tz': 'UTC'},
    'tables': [
        {
            'target': 'location',
            'source': 'LOCATION',
            'key': ['id'],
            'columns': {'id': 'ID', 'unlocode': 'UNLOCODE', 'name': 'NAME'},
        },
        {
            'target': 'voyage',
            'source': 'VOYAGE',
            'key': ['id'],
            'columns': {'id': 'ID', 'voyage_number': 'VOYAGE_NUMBER'},
        },
        {
            'target': 'cargo',
            'source': 'CARGO',
            'key': ['id'],
            'columns': {
                'id': 'ID',
                'tracking_id': 'TRACKING_ID',
                'origin_id': 'ORIGIN_ID',
                'spec_origin_id': 'SPEC_ORIGIN_ID',
                'spec_destination_id': 'SPEC_DESTINATION_ID',
                'spec_arrival_deadline': {'from': 'SPEC_ARRIVAL_DEADLINE', 'as': 'date'},
                'transport_status': 'TRANSPORT_STATUS',
                'last_known_location_id': 'LAST_KNOWN_LOCATION_ID',
                'current_voyage_id': 'CURRENT_VOYAGE_ID',
                'misdirected': {'from': 'MISDIRECTED', 'as': 'bool'},
                'eta': {'from': 'ETA', 'as': 'date'},
                'next_expected_handling_event_type': 'NEXT_EXPECTED_HANDLING_EVENT_TYPE',
                'next_expected_location_id': 'NEXT_EXPECTED_LOCATION_ID',
                'next_expected_voyage_id': 'NEXT_EXPECTED_VOYAGE_ID',
                'unloaded_at_dest': {'from': 'UNLOADED_AT_DEST', 'as': 'bool'},
                'routing_status': 'ROUTING_STATUS',
                'calculated_at': {'from': 'CALCULATED_AT', 'as': 'timestamp'},
            },
            'refs': {
                'origin_id': 'location.id',
                'spec_origin_id': 'location.id',
                'spec_destination_id': 'location.id',
                'last_known_location_id': 'location.id',
                'current_voyage_id': 'voyage.id',
                'next_expected_location_id': 'location.id',
                'next_expected_voyage_id': 'voyage.id',
            },
        },
    ],
}


@pytest.mark.django_db(transaction=True)
def test_export_data_snapshot_round_trips_mapped_fixture_rows(tmp_path):
    mapping_path = tmp_path / 'mapping.yaml'
    mapping_path.write_text(yaml.safe_dump(MAPPING, sort_keys=False), encoding='utf-8')
    call_command('load_data_snapshot', snapshot=str(SNAPSHOT), mapping=str(mapping_path))
    LocationRecord.objects.create(id=104, unlocode='TST04', name='Fourth')
    LocationRecord.objects.create(id=103, unlocode='TST03', name='Third')

    output = tmp_path / 'export'
    call_command('export_data_snapshot', mapping=str(mapping_path), out=str(output))

    exported = {}
    for spec in MAPPING['tables']:
        with (output / f'{spec["target"]}.csv').open(newline='', encoding='utf-8') as stream:
            reader = csv.DictReader(stream)
            assert reader.fieldnames == list(spec['columns'])
            rows = list(reader)
        with (SNAPSHOT / f'{spec["source"]}.csv').open(newline='', encoding='utf-8') as stream:
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
