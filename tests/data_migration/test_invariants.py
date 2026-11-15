import csv
import hashlib
import json
import shutil
from datetime import UTC, datetime, time
from itertools import pairwise
from pathlib import Path

import pytest
from django.core.management import call_command

from cargotracker.cargo.domain.cargo import Cargo
from cargotracker.cargo.domain.delivery import Delivery, RoutingStatus, TransportStatus
from cargotracker.cargo.domain.handling_activity import HandlingActivity
from cargotracker.cargo.domain.itinerary import Itinerary
from cargotracker.cargo.domain.leg import Leg
from cargotracker.cargo.domain.route_specification import RouteSpecification
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.models import CargoRecord, LegRecord
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

FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = Path(__file__).resolve().parents[2] / '.migration' / 'data' / 'mapping.yaml'


def _read_rows(snapshot, table):
    with (snapshot / f'{table}.csv').open(encoding='utf-8', newline='') as stream:
        return list(csv.DictReader(stream))


def _write_rows(snapshot, table, rows):
    path = snapshot / f'{table}.csv'
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest['tables'][table].update(
        rows=len(rows),
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
    )
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')


def _domain_references():
    locations = {
        record.pk: Location(UnLocode(record.unlocode), record.name)
        for record in LocationRecord.objects.all()
    }
    voyages = {
        record.pk: Voyage(VoyageNumber(record.voyage_number), Schedule.EMPTY)
        for record in VoyageRecord.objects.all()
    }
    return (
        locations,
        voyages,
        {location: pk for pk, location in locations.items()},
        {voyage: pk for pk, voyage in voyages.items()},
    )


def _derive_delivery(cargo_record, locations, voyages):
    route_specification = RouteSpecification(
        origin=locations[cargo_record.spec_origin_id],
        destination=locations[cargo_record.spec_destination_id],
        arrival_deadline=datetime.combine(cargo_record.spec_arrival_deadline, time.min, tzinfo=UTC),
    )
    legs = [
        Leg(
            voyage=voyages[record.voyage_id],
            load_location=locations[record.load_location_id],
            unload_location=locations[record.unload_location_id],
            load_time=record.load_time,
            unload_time=record.unload_time,
        )
        for record in LegRecord.objects.filter(cargo_id=cargo_record.pk).order_by('load_time', 'pk')
    ]
    itinerary = Itinerary(legs)
    cargo = Cargo(
        tracking_id=TrackingId(cargo_record.tracking_id),
        route_specification=route_specification,
        delivery=Delivery(
            transport_status=TransportStatus.UNKNOWN,
            last_known_location=None,
            current_voyage=None,
            misdirected=False,
            eta=None,
            next_expected_activity=HandlingActivity.EMPTY,
            unloaded_at_destination=False,
            routing_status=RoutingStatus.NOT_ROUTED,
            calculated_at=cargo_record.calculated_at,
        ),
        itinerary=itinerary,
    )
    events = [
        HandlingEvent(
            cargo=cargo,
            completion_time=record.completion_time,
            registration_time=record.registration_time,
            event_type=HandlingEventType(record.event_type),
            location=locations[record.location_id],
            voyage=voyages.get(record.voyage_id),
            id=record.pk,
        )
        for record in HandlingEventRecord.objects.filter(cargo_id=cargo_record.pk).order_by(
            'completion_time', 'registration_time', 'pk'
        )
    ]
    history = HandlingHistory(events, event_ids=[event.id for event in events])
    delivery = Delivery.derived_from(
        route_specification,
        itinerary,
        history,
        calculated_at=cargo_record.calculated_at,
    )
    return delivery, history


@pytest.fixture
def loaded_snapshot(tmp_path):
    snapshot = tmp_path / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)

    cargo_rows = _read_rows(snapshot, 'CARGO')
    cargo_rows[0].update(
        TRANSPORT_STATUS='ONBOARD_CARRIER',
        LAST_KNOWN_LOCATION_ID='101',
        CURRENT_VOYAGE_ID='900',
        MISDIRECTED='false',
        ETA='2026-11-11',
        NEXT_EXPECTED_HANDLING_EVENT_TYPE='UNLOAD',
        NEXT_EXPECTED_LOCATION_ID='102',
        NEXT_EXPECTED_VOYAGE_ID='900',
        SPEC_DESTINATION_ID='103',
        ROUTING_STATUS='ROUTED',
    )
    _write_rows(snapshot, 'CARGO', cargo_rows)

    locations = _read_rows(snapshot, 'LOCATION')
    locations.append({'ID': '103', 'UNLOCODE': 'SGSIN', 'NAME': 'Singapore'})
    _write_rows(snapshot, 'LOCATION', locations)

    events = _read_rows(snapshot, 'HANDLINGEVENT')
    events[0].update(TYPE='LOAD', LOCATION_ID='101')
    _write_rows(snapshot, 'HANDLINGEVENT', events)

    legs = _read_rows(snapshot, 'LEG')
    legs[0].update(
        LOAD_TIME='2026-11-08T12:00:00Z',
        UNLOAD_TIME='2026-11-09T12:00:00Z',
    )
    legs.append(
        {
            'ID': '82',
            'LOAD_TIME': '2026-11-10T12:00:00Z',
            'UNLOAD_TIME': '2026-11-11T12:00:00Z',
            'LOAD_LOCATION_ID': '102',
            'UNLOAD_LOCATION_ID': '103',
            'VOYAGE_ID': '900',
            'CARGO_ID': '13',
        }
    )
    _write_rows(snapshot, 'LEG', legs)

    movements = _read_rows(snapshot, 'CARRIER_MOVEMENT')
    movements[0].update(
        ARRIVAL_TIME='2026-11-09T12:00:00Z',
        DEPARTURE_TIME='2026-11-08T12:00:00Z',
    )
    movements.append(
        {
            'ID': '92',
            'ARRIVAL_TIME': '2026-11-11T12:00:00Z',
            'DEPARTURE_TIME': '2026-11-10T12:00:00Z',
            'ARRIVAL_LOCATION_ID': '103',
            'DEPARTURE_LOCATION_ID': '102',
            'VOYAGE_ID': '900',
        }
    )
    _write_rows(snapshot, 'CARRIER_MOVEMENT', movements)

    call_command('load_data_snapshot', snapshot=str(snapshot), mapping=str(MAPPING))
    return snapshot


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_state_matches_its_handling_history(loaded_snapshot):
    assert CargoRecord.objects.exists()
    locations, voyages, location_ids, voyage_ids = _domain_references()

    for cargo in CargoRecord.objects.order_by('pk'):
        delivery, history = _derive_delivery(cargo, locations, voyages)
        assert cargo.transport_status == delivery.transport_status
        assert cargo.last_known_location_id == location_ids.get(delivery.last_known_location)
        assert cargo.current_voyage_id == voyage_ids.get(delivery.current_voyage)
        assert cargo.misdirected == delivery.misdirected
        assert cargo.eta == (delivery.eta.date() if delivery.eta else None)
        assert cargo.next_expected_handling_event_type == delivery.next_expected_activity.event_type
        assert cargo.next_expected_location_id == location_ids.get(
            delivery.next_expected_activity.location
        )
        assert cargo.next_expected_voyage_id == voyage_ids.get(
            delivery.next_expected_activity.voyage
        )
        assert cargo.unloaded_at_dest == delivery.unloaded_at_destination
        assert cargo.routing_status == delivery.routing_status
        assert cargo.last_event_id == history.most_recent_event_id


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(loaded_snapshot):
    assert LegRecord.objects.count() > 1

    for cargo in CargoRecord.objects.order_by('pk'):
        legs = list(LegRecord.objects.filter(cargo_id=cargo.pk).order_by('load_time', 'pk'))
        assert all(
            previous.unload_location_id == following.load_location_id
            for previous, following in pairwise(legs)
        )


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_events_reference_existing_voyages_and_locations(loaded_snapshot):
    assert HandlingEventRecord.objects.exists()

    for event in HandlingEventRecord.objects.all():
        assert event.voyage_id is not None
        assert VoyageRecord.objects.filter(pk=event.voyage_id).exists()
        assert event.location_id is not None
        assert LocationRecord.objects.filter(pk=event.location_id).exists()


@pytest.mark.django_db(transaction=True)
def test_loaded_voyage_schedules_are_in_order(loaded_snapshot):
    assert CarrierMovementRecord.objects.count() > 1

    for voyage in VoyageRecord.objects.order_by('pk'):
        movements = list(
            CarrierMovementRecord.objects.filter(voyage_id=voyage.pk).order_by(
                'departure_time', 'pk'
            )
        )
        assert all(movement.departure_time <= movement.arrival_time for movement in movements)
        assert all(
            previous.arrival_time <= following.departure_time
            for previous, following in pairwise(movements)
        )
