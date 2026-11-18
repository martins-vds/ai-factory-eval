import csv
import hashlib
import json
from dataclasses import replace
from itertools import pairwise
from pathlib import Path

import pytest
from django.core.management import call_command

from cargotracker.cargo.domain.delivery import Delivery
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.models import CargoRecord
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.models import HandlingEventRecord
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.models import LocationRecord
from cargotracker.voyage.infrastructure.models import CarrierMovementRecord, VoyageRecord

SNAPSHOT_TABLES = {
    'LOCATION': (
        ('ID', 'UNLOCODE', 'NAME'),
        (
            ('101', 'USNYC', 'New York'),
            ('102', 'NLRTM', 'Rotterdam'),
            ('103', 'DEHAM', 'Hamburg'),
        ),
    ),
    'VOYAGE': (('ID', 'VOYAGE_NUMBER'), (('900', 'V001'),)),
    'CARGO': (
        (
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
        ),
        (
            (
                '13',
                'FIDELITY-0001',
                '101',
                '101',
                '103',
                '2026-12-30',
                'ONBOARD_CARRIER',
                '101',
                '900',
                'false',
                '2026-11-11',
                'UNLOAD',
                '102',
                '900',
                'false',
                'ROUTED',
                '2026-11-08T13:02:00Z',
                '71',
            ),
        ),
    ),
    'HANDLINGEVENT': (
        (
            'ID',
            'TYPE',
            'VOYAGE_ID',
            'LOCATION_ID',
            'COMPLETIONTIME',
            'REGISTRATION',
            'CARGO_ID',
        ),
        (
            ('71', 'LOAD', '900', '101', '2026-11-08T13:00:00Z', '2026-11-08T13:01:00Z', '13'),
            ('72', 'RECEIVE', None, '101', '2026-11-08T12:30:00Z', '2026-11-08T12:31:00Z', '13'),
        ),
    ),
    'LEG': (
        (
            'ID',
            'LOAD_TIME',
            'UNLOAD_TIME',
            'LOAD_LOCATION_ID',
            'UNLOAD_LOCATION_ID',
            'VOYAGE_ID',
            'CARGO_ID',
        ),
        (
            ('81', '2026-11-08T12:00:00Z', '2026-11-09T12:00:00Z', '101', '102', '900', '13'),
            ('82', '2026-11-10T12:00:00Z', '2026-11-11T12:00:00Z', '102', '103', '900', '13'),
        ),
    ),
    'CARRIER_MOVEMENT': (
        (
            'ID',
            'ARRIVAL_TIME',
            'DEPARTURE_TIME',
            'ARRIVAL_LOCATION_ID',
            'DEPARTURE_LOCATION_ID',
            'VOYAGE_ID',
        ),
        (
            ('91', '2026-11-09T12:00:00Z', '2026-11-08T12:00:00Z', '102', '101', '900'),
            ('92', '2026-11-11T12:00:00Z', '2026-11-10T12:00:00Z', '103', '102', '900'),
        ),
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


@pytest.fixture
def loaded_snapshot(tmp_path):
    snapshot = tmp_path / 'snapshot'
    _write_snapshot(snapshot)
    mapping = Path(__file__).resolve().parents[2] / '.migration' / 'data' / 'mapping.yaml'
    call_command(
        'load_data_snapshot',
        snapshot=str(snapshot),
        mapping=str(mapping),
    )
    return snapshot


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_matches_its_handling_history(loaded_snapshot):
    records = CargoRecord.objects.all()
    assert records.exists()

    cargos = DjangoCargoRepository()
    events = DjangoHandlingEventRepository()
    for record in records:
        cargo = cargos.find(TrackingId(record.tracking_id))
        assert cargo is not None
        history = events.lookup_handling_history_of_cargo(cargo.tracking_id)
        derived = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            calculated_at=cargo.delivery.calculated_at,
        )
        derived = replace(derived, last_event_id=history.most_recent_event_id)

        assert cargo.delivery.transport_status == derived.transport_status
        assert cargo.delivery.last_known_location == derived.last_known_location
        assert cargo.delivery.current_voyage == derived.current_voyage
        assert cargo.delivery.misdirected == derived.misdirected
        assert (cargo.delivery.eta.date() if cargo.delivery.eta is not None else None) == (
            derived.eta.date() if derived.eta is not None else None
        )
        assert cargo.delivery.next_expected_activity == derived.next_expected_activity
        assert cargo.delivery.unloaded_at_destination == derived.unloaded_at_destination
        assert cargo.delivery.routing_status == derived.routing_status
        assert cargo.delivery.last_event_id == derived.last_event_id


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(loaded_snapshot):
    cargos = CargoRecord.objects.prefetch_related('legs')
    assert cargos.exists()

    for cargo in cargos:
        legs = list(cargo.legs.all())
        assert legs
        assert all(
            first.unload_location_id == second.load_location_id for first, second in pairwise(legs)
        )


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_events_reference_existing_voyages_and_locations(loaded_snapshot):
    event_references = list(
        HandlingEventRecord.objects.values_list('event_type', 'voyage_id', 'location_id')
    )
    voyage_ids = set(VoyageRecord.objects.values_list('pk', flat=True))
    location_ids = set(LocationRecord.objects.values_list('pk', flat=True))
    assert event_references

    for event_type, voyage_id, location_id in event_references:
        assert (event_type in {'LOAD', 'UNLOAD'}) == (voyage_id is not None)
        if voyage_id is not None:
            assert voyage_id in voyage_ids
        assert location_id in location_ids


@pytest.mark.django_db(transaction=True)
def test_loaded_non_carrier_handling_event_keeps_null_voyage(loaded_snapshot):
    event = HandlingEventRecord.objects.get(event_type='RECEIVE')

    assert event.voyage_id is None


@pytest.mark.django_db(transaction=True)
def test_loaded_voyage_carrier_movements_are_in_schedule_order(loaded_snapshot):
    voyages = VoyageRecord.objects.all()
    assert voyages.exists()

    for voyage in voyages:
        movements = list(
            CarrierMovementRecord.objects.filter(voyage=voyage).order_by('departure_time')
        )
        assert movements
        assert all(movement.departure_time < movement.arrival_time for movement in movements)
        assert all(
            first.arrival_time <= second.departure_time for first, second in pairwise(movements)
        )
