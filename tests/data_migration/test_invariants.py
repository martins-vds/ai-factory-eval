import csv
import hashlib
import json
from dataclasses import replace
from itertools import groupby, pairwise
from pathlib import Path

import pytest
from django.core.management import call_command

from cargotracker.cargo.domain.delivery import Delivery
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.domain.handling_event import HandlingEvent, HandlingEventType
from cargotracker.handling.domain.handling_history import HandlingHistory
from cargotracker.handling.infrastructure.models import HandlingEventRecord
from cargotracker.location.domain.location import Location
from cargotracker.location.domain.un_locode import UnLocode
from cargotracker.location.infrastructure.models import LocationRecord
from cargotracker.voyage.domain.schedule import Schedule
from cargotracker.voyage.domain.voyage import Voyage
from cargotracker.voyage.domain.voyage_number import VoyageNumber
from cargotracker.voyage.infrastructure.models import CarrierMovementRecord, VoyageRecord

MAPPING_PATH = Path(__file__).resolve().parents[2] / '.migration' / 'data' / 'mapping.yaml'

SNAPSHOT_TABLES = {
    'LOCATION': (
        ['ID', 'UNLOCODE', 'NAME'],
        [
            ['1', 'USNYC', 'New York'],
            ['2', 'NLRTM', 'Rotterdam'],
            ['3', 'SGSIN', 'Singapore'],
        ],
    ),
    'VOYAGE': (
        ['ID', 'VOYAGE_NUMBER'],
        [['900', 'V-900'], ['901', 'V-901'], ['902', 'V-902']],
    ),
    'CARGO': (
        [
            'ID',
            'TRACKING_ID',
            'ORIGIN_ID',
            'SPEC_ORIGIN_ID',
            'SPEC_DESTINATION_ID',
            'SPEC_ARRIVAL_DEADLINE',
            'TRANSPORT_STATUS',
            'LAST_KNOWN_LOCATION_ID',
            'CURRENT_VOYAGE_ID',
            'MISDIRECTED',
            'ETA',
            'NEXT_EXPECTED_HANDLING_EVENT_TYPE',
            'NEXT_EXPECTED_LOCATION_ID',
            'NEXT_EXPECTED_VOYAGE_ID',
            'UNLOADED_AT_DEST',
            'ROUTING_STATUS',
            'CALCULATED_AT',
            'LAST_EVENT_ID',
        ],
        [
            [
                '301',
                'DM-05F-001',
                '1',
                '1',
                '3',
                '2026-11-10',
                'ONBOARD_CARRIER',
                '1',
                '901',
                'false',
                '2026-11-09',
                'UNLOAD',
                '2',
                '901',
                'false',
                'ROUTED',
                '2026-11-07T12:00:00Z',
                '701',
            ]
        ],
    ),
    'HANDLINGEVENT': (
        [
            'ID',
            'TYPE',
            'VOYAGE_ID',
            'LOCATION_ID',
            'COMPLETIONTIME',
            'REGISTRATION',
            'CARGO_ID',
        ],
        [
            ['700', 'RECEIVE', None, '1', '2026-11-07T08:30:00Z', '2026-11-07T08:31:00Z', '301'],
            ['701', 'LOAD', '901', '1', '2026-11-07T09:00:00Z', '2026-11-07T09:01:00Z', '301'],
        ],
    ),
    'LEG': (
        [
            'ID',
            'LOAD_TIME',
            'UNLOAD_TIME',
            'LOAD_LOCATION_ID',
            'UNLOAD_LOCATION_ID',
            'VOYAGE_ID',
            'CARGO_ID',
        ],
        [
            ['801', '2026-11-07T09:00:00Z', '2026-11-07T10:00:00Z', '1', '2', '901', '301'],
            ['802', '2026-11-07T11:00:00Z', '2026-11-09T00:00:00Z', '2', '3', '902', '301'],
        ],
    ),
    'CARRIER_MOVEMENT': (
        [
            'ID',
            'ARRIVAL_TIME',
            'DEPARTURE_TIME',
            'ARRIVAL_LOCATION_ID',
            'DEPARTURE_LOCATION_ID',
            'VOYAGE_ID',
        ],
        [
            ['1000', '2026-11-07T09:00:00Z', '2026-11-07T08:00:00Z', '2', '1', '900'],
            ['1001', '2026-11-07T10:00:00Z', '2026-11-07T09:00:00Z', '3', '2', '900'],
            ['1002', '2026-11-07T10:00:00Z', '2026-11-07T09:00:00Z', '2', '1', '901'],
            ['1003', '2026-11-09T00:00:00Z', '2026-11-07T11:00:00Z', '3', '2', '902'],
        ],
    ),
    'SEQUENCE': (['SEQ_NAME', 'SEQ_COUNT'], [['unused', '1']]),
}

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def loaded_snapshot(tmp_path):
    snapshot = tmp_path / 'snapshot'
    snapshot.mkdir()
    tables = {}
    for table, (header, rows) in SNAPSHOT_TABLES.items():
        path = snapshot / f'{table}.csv'
        with path.open('w', encoding='utf-8', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(header)
            writer.writerows([['\\N' if value is None else value for value in row] for row in rows])
        tables[table] = {
            'rows': len(rows),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    (snapshot / 'manifest.json').write_text(
        json.dumps({'null': '\\N', 'tables': tables}),
        encoding='utf-8',
    )
    call_command(
        'load_data_snapshot',
        snapshot=str(snapshot),
        mapping=str(MAPPING_PATH),
    )


def _location(record):
    return Location(UnLocode(record.unlocode), record.name)


def _voyage(record):
    return Voyage(VoyageNumber(record.voyage_number), Schedule.EMPTY)


def test_loaded_cargo_delivery_state_matches_its_handling_history(loaded_snapshot):
    cargo = DjangoCargoRepository().find(TrackingId('DM-05F-001'))
    assert cargo is not None
    records = list(
        HandlingEventRecord.objects.filter(cargo_id=301)
        .select_related('location', 'voyage')
        .order_by('completion_time', 'registration_time', 'pk')
    )
    events = [
        HandlingEvent(
            cargo=cargo,
            completion_time=record.completion_time,
            registration_time=record.registration_time,
            event_type=HandlingEventType(record.event_type),
            location=_location(record.location),
            voyage=_voyage(record.voyage) if record.voyage is not None else None,
            id=record.pk,
        )
        for record in records
    ]
    history = HandlingHistory(events, [record.pk for record in records])
    derived = Delivery.derived_from(
        cargo.route_specification,
        cargo.itinerary,
        history,
        calculated_at=cargo.delivery.calculated_at,
    )

    assert cargo.delivery == replace(derived, last_event_id=history.most_recent_event_id)


def test_loaded_itinerary_legs_connect(loaded_snapshot):
    cargos = DjangoCargoRepository().find_all()
    assert cargos

    for cargo in cargos:
        for previous, following in pairwise(cargo.itinerary.legs):
            assert previous.unload_location == following.load_location


def test_loaded_handling_events_reference_existing_voyages_and_locations(loaded_snapshot):
    location_ids = set(LocationRecord.objects.values_list('pk', flat=True))
    voyage_ids = set(VoyageRecord.objects.values_list('pk', flat=True))
    events = list(HandlingEventRecord.objects.all())
    assert events

    for event in events:
        assert event.location_id in location_ids
        if event.voyage_id is not None:
            assert event.voyage_id in voyage_ids
        assert HandlingEventType(event.event_type).requires_voyage == (event.voyage_id is not None)


def test_loaded_carrier_movement_schedules_are_contiguous_and_chronological(loaded_snapshot):
    schedules = (
        list(movements)
        for _, movements in groupby(
            CarrierMovementRecord.objects.order_by('voyage_id', 'departure_time', 'pk'),
            key=lambda movement: movement.voyage_id,
        )
    )
    schedules = list(schedules)
    assert any(len(schedule) > 1 for schedule in schedules)

    for schedule in schedules:
        for movement in schedule:
            assert movement.departure_time <= movement.arrival_time
        for previous, following in pairwise(schedule):
            assert previous.arrival_time <= following.departure_time
            assert previous.arrival_location_id == following.departure_location_id
