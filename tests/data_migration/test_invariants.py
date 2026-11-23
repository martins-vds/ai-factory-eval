import csv
import hashlib
import json
from itertools import pairwise
from pathlib import Path

import pytest
from django.core.management import call_command

from cargotracker.cargo.domain.delivery import Delivery
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.models import CargoRecord, LegRecord
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
from cargotracker.voyage.infrastructure.models import (
    CarrierMovementRecord,
    VoyageRecord,
)

ROOT = Path(__file__).resolve().parents[2]
MAPPING = ROOT / '.migration' / 'data' / 'mapping.yaml'

SNAPSHOT_ROWS = {
    'LOCATION': (
        ['ID', 'UNLOCODE', 'NAME'],
        [
            ['101', 'USNYC', 'New York'],
            ['102', 'NLRTM', 'Rotterdam'],
            ['103', 'USCHI', 'Chicago'],
            ['104', 'USLAX', 'Los Angeles'],
            ['105', 'USSEA', 'Seattle'],
        ],
    ),
    'VOYAGE': (
        ['ID', 'VOYAGE_NUMBER'],
        [['900', 'V001'], ['901', 'V002']],
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
                '13',
                'FIDELITY-0001',
                '101',
                '101',
                '102',
                '2026-12-01',
                'ONBOARD_CARRIER',
                '101',
                '900',
                'false',
                '2026-11-11',
                'UNLOAD',
                '103',
                '900',
                'false',
                'ROUTED',
                '2026-11-08T10:01:00Z',
                '72',
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
            ['71', 'RECEIVE', r'\N', '101', '2026-11-07T08:00:00Z', '2026-11-07T08:01:00Z', '13'],
            ['72', 'LOAD', '900', '101', '2026-11-08T10:00:00Z', '2026-11-08T10:01:00Z', '13'],
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
            ['81', '2026-11-08T10:00:00Z', '2026-11-08T18:00:00Z', '101', '103', '900', '13'],
            ['82', '2026-11-09T09:00:00Z', '2026-11-09T17:00:00Z', '103', '104', '900', '13'],
            ['83', '2026-11-10T09:00:00Z', '2026-11-10T17:00:00Z', '104', '105', '901', '13'],
            ['84', '2026-11-11T09:00:00Z', '2026-11-11T17:00:00Z', '105', '102', '901', '13'],
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
            ['91', '2026-11-08T18:00:00Z', '2026-11-08T10:00:00Z', '103', '101', '900'],
            ['92', '2026-11-09T17:00:00Z', '2026-11-09T09:00:00Z', '104', '103', '900'],
            ['93', '2026-11-10T17:00:00Z', '2026-11-10T09:00:00Z', '105', '104', '901'],
            ['94', '2026-11-11T17:00:00Z', '2026-11-11T09:00:00Z', '102', '105', '901'],
        ],
    ),
}


def _load_snapshot(tmp_path):
    snapshot = tmp_path / 'snapshot'
    snapshot.mkdir()
    tables = {}
    for table, (header, rows) in SNAPSHOT_ROWS.items():
        path = snapshot / f'{table}.csv'
        with path.open('w', encoding='utf-8', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(header)
            writer.writerows(rows)
        tables[table] = {
            'rows': len(rows),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    (snapshot / 'manifest.json').write_text(
        json.dumps({'null': r'\N', 'tables': tables}),
        encoding='utf-8',
    )
    call_command('load_data_snapshot', snapshot=str(snapshot), mapping=str(MAPPING))


def _location(record):
    return Location(UnLocode(record.unlocode), record.name)


def _voyage(record):
    return Voyage(VoyageNumber(record.voyage_number), Schedule.EMPTY)


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_matches_its_handling_history(tmp_path):
    _load_snapshot(tmp_path)
    record = CargoRecord.objects.get(tracking_id='FIDELITY-0001')
    cargo = DjangoCargoRepository().find(TrackingId(record.tracking_id))
    rows = (
        HandlingEventRecord.objects.filter(cargo_id=record.pk)
        .select_related('location', 'voyage')
        .order_by('completion_time', 'registration_time', 'pk')
    )
    events = [
        HandlingEvent(
            cargo=cargo,
            completion_time=row.completion_time,
            registration_time=row.registration_time,
            event_type=HandlingEventType(row.event_type),
            location=_location(row.location),
            voyage=_voyage(row.voyage) if row.voyage_id is not None else None,
        )
        for row in rows
    ]
    history = HandlingHistory(events, rows.values_list('pk', flat=True))
    derived = Delivery.derived_from(
        cargo.route_specification,
        cargo.itinerary,
        history,
        calculated_at=cargo.delivery.calculated_at,
    )

    assert cargo.delivery.transport_status == derived.transport_status
    assert cargo.delivery.last_known_location == derived.last_known_location
    assert cargo.delivery.current_voyage == derived.current_voyage
    assert cargo.delivery.misdirected == derived.misdirected
    assert (cargo.delivery.eta.date() if cargo.delivery.eta else None) == (
        derived.eta.date() if derived.eta else None
    )
    assert cargo.delivery.next_expected_activity == derived.next_expected_activity
    assert cargo.delivery.unloaded_at_destination == derived.unloaded_at_destination
    assert cargo.delivery.routing_status == derived.routing_status
    assert cargo.delivery.last_event_id == history.most_recent_event_id


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(tmp_path):
    _load_snapshot(tmp_path)

    for cargo in CargoRecord.objects.all():
        legs = list(LegRecord.objects.filter(cargo=cargo).order_by('load_time', 'pk'))
        for previous, following in pairwise(legs):
            assert previous.unload_location_id == following.load_location_id


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_events_reference_existing_voyages_and_locations(tmp_path):
    _load_snapshot(tmp_path)

    for event in HandlingEventRecord.objects.all():
        assert LocationRecord.objects.filter(pk=event.location_id).exists()
        if event.voyage_id is not None:
            assert VoyageRecord.objects.filter(pk=event.voyage_id).exists()


@pytest.mark.django_db(transaction=True)
def test_loaded_carrier_movement_schedules_are_in_order(tmp_path):
    _load_snapshot(tmp_path)

    for voyage in VoyageRecord.objects.all():
        movements = list(
            CarrierMovementRecord.objects.filter(voyage=voyage).order_by('departure_time', 'pk')
        )
        assert movements
        assert all(movement.departure_time <= movement.arrival_time for movement in movements)
        for previous, following in pairwise(movements):
            assert previous.arrival_time <= following.departure_time
            assert previous.arrival_location_id == following.departure_location_id
