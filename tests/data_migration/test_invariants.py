import csv
import hashlib
import json
from dataclasses import replace
from pathlib import Path

import pytest
from django.core.management import call_command

from cargotracker.cargo.domain.delivery import Delivery
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.models import CargoRecord, LegRecord
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.models import HandlingEventRecord
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.models import LocationRecord
from cargotracker.voyage.infrastructure.models import CarrierMovementRecord, VoyageRecord


SNAPSHOT_TABLES = {
    'LOCATION': (
        ['ID', 'UNLOCODE', 'NAME'],
        [
            ['1', 'USNYC', 'New York'],
            ['2', 'NLRTM', 'Rotterdam'],
            ['3', 'FIHEL', 'Helsinki'],
        ],
    ),
    'VOYAGE': (['ID', 'VOYAGE_NUMBER'], [['10', 'V001']]),
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
                '20',
                'INVARIANT-0001',
                '1',
                '1',
                '3',
                '2026-11-10',
                'IN_PORT',
                '1',
                None,
                'false',
                '2026-11-09',
                'LOAD',
                '1',
                '10',
                'false',
                'ROUTED',
                '2026-11-07T10:11:12Z',
                '31',
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
        [['31', 'RECEIVE', None, '1', '2026-11-07T10:00:00Z', '2026-11-07T10:01:00Z', '20']],
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
            ['42', '2026-11-08T13:00:00Z', '2026-11-09T00:00:00Z', '2', '3', '10', '20'],
            ['41', '2026-11-08T08:00:00Z', '2026-11-08T12:00:00Z', '1', '2', '10', '20'],
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
            ['52', '2026-11-09T00:00:00Z', '2026-11-08T13:00:00Z', '3', '2', '10'],
            ['51', '2026-11-08T12:00:00Z', '2026-11-08T08:00:00Z', '2', '1', '10'],
        ],
    ),
}


def _write_snapshot(snapshot):
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


def _load_snapshot(tmp_path):
    snapshot = tmp_path / 'snapshot'
    _write_snapshot(snapshot)
    mapping = Path(__file__).resolve().parents[2] / '.migration' / 'data' / 'mapping.yaml'
    call_command('load_data_snapshot', snapshot=str(snapshot), mapping=str(mapping))


pytestmark = pytest.mark.django_db(transaction=True)


def test_loaded_cargo_delivery_matches_its_handling_history(tmp_path):
    _load_snapshot(tmp_path)

    cargo = DjangoCargoRepository().find(TrackingId('INVARIANT-0001'))
    history = DjangoHandlingEventRepository().lookup_handling_history_of_cargo(cargo.tracking_id)
    derived_delivery = Delivery.derived_from(
        cargo.route_specification,
        cargo.itinerary,
        history,
        calculated_at=cargo.delivery.calculated_at,
    )

    assert cargo.delivery == replace(
        derived_delivery,
        last_event_id=history.most_recent_event_id,
    )


def test_loaded_itinerary_legs_connect(tmp_path):
    _load_snapshot(tmp_path)

    for cargo in CargoRecord.objects.all():
        legs = list(cargo.legs.order_by('load_time', 'pk'))
        assert len(legs) >= 2
        assert all(
            previous.unload_location_id == following.load_location_id
            for previous, following in zip(legs, legs[1:])
        )


def test_loaded_handling_events_reference_existing_voyages_and_locations(tmp_path):
    _load_snapshot(tmp_path)

    location_ids = set(LocationRecord.objects.values_list('pk', flat=True))
    voyage_ids = set(VoyageRecord.objects.values_list('pk', flat=True))
    events = HandlingEventRecord.objects.all()

    assert events.exists()
    assert all(event.location_id in location_ids for event in events)
    assert all(event.voyage_id is None or event.voyage_id in voyage_ids for event in events)


def test_loaded_carrier_movement_schedules_are_in_order(tmp_path):
    _load_snapshot(tmp_path)

    for voyage in VoyageRecord.objects.all():
        movements = list(
            CarrierMovementRecord.objects.filter(voyage=voyage).order_by('departure_time', 'pk')
        )
        assert len(movements) >= 2
        assert all(movement.departure_time <= movement.arrival_time for movement in movements)
        assert all(
            previous.arrival_time <= following.departure_time
            and previous.arrival_location_id == following.departure_location_id
            for previous, following in zip(movements, movements[1:])
        )
