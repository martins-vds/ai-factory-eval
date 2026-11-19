import csv
import hashlib
import json
import shutil
from collections import defaultdict
from datetime import UTC, datetime
from itertools import pairwise
from pathlib import Path

import pytest
import yaml
from django.core.management import call_command
from tests.data_migration.test_load import FIXTURE_SNAPSHOT, MAPPING

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


def _load_fixture(tmp_path: Path) -> None:
    snapshot = tmp_path / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)
    _rewrite_snapshot(
        snapshot,
        'CARGO',
        {
            'TRANSPORT_STATUS': 'IN_PORT',
            'LAST_KNOWN_LOCATION_ID': '101',
            'CURRENT_VOYAGE_ID': '\\N',
            'MISDIRECTED': 'false',
            'ETA': '2026-11-09',
            'NEXT_EXPECTED_HANDLING_EVENT_TYPE': 'LOAD',
            'NEXT_EXPECTED_LOCATION_ID': '101',
            'NEXT_EXPECTED_VOYAGE_ID': '900',
        },
    )
    _rewrite_snapshot(snapshot, 'HANDLINGEVENT', {'LOCATION_ID': '101'})
    mapping = tmp_path / 'mapping.yaml'
    mapping.write_text(yaml.safe_dump(MAPPING), encoding='utf-8')
    call_command(
        'load_data_snapshot',
        snapshot=str(snapshot),
        mapping=str(mapping),
    )


def _rewrite_snapshot(snapshot: Path, table: str, updates: dict[str, str]) -> None:
    path = snapshot / f'{table}.csv'
    with path.open(newline='', encoding='utf-8') as stream:
        rows = list(csv.DictReader(stream))
        fieldnames = rows[0].keys()
    rows[0].update(updates)
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest['tables'][table]['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')


def _handling_event(record: HandlingEventRecord, cargo) -> HandlingEvent:
    return HandlingEvent(
        cargo=cargo,
        completion_time=record.completion_time,
        registration_time=record.registration_time,
        event_type=HandlingEventType(record.event_type),
        location=Location(UnLocode(record.location.unlocode), record.location.name),
        voyage=(
            Voyage(VoyageNumber(record.voyage.voyage_number), Schedule.EMPTY)
            if record.voyage_id and record.event_type in {'LOAD', 'UNLOAD'}
            else None
        ),
        id=record.id,
    )


def _domain_location(record: LocationRecord) -> Location:
    return Location(UnLocode(record.unlocode), record.name)


def _domain_voyage(record: VoyageRecord) -> Voyage:
    return Voyage(VoyageNumber(record.voyage_number), Schedule.EMPTY)


def _domain_cargo(record: CargoRecord) -> Cargo:
    legs = [
        Leg(
            _domain_voyage(leg.voyage),
            _domain_location(leg.load_location),
            _domain_location(leg.unload_location),
            leg.load_time,
            leg.unload_time,
        )
        for leg in LegRecord.objects.filter(cargo=record).select_related(
            'voyage', 'load_location', 'unload_location'
        )
    ]
    return Cargo(
        tracking_id=TrackingId(record.tracking_id),
        route_specification=RouteSpecification(
            _domain_location(record.spec_origin),
            _domain_location(record.spec_destination),
            datetime.combine(record.spec_arrival_deadline, datetime.min.time(), tzinfo=UTC),
        ),
        delivery=Delivery(
            transport_status=TransportStatus(record.transport_status),
            last_known_location=(
                _domain_location(record.last_known_location)
                if record.last_known_location_id
                else None
            ),
            current_voyage=(
                _domain_voyage(record.current_voyage) if record.current_voyage_id else None
            ),
            misdirected=record.misdirected,
            eta=None,
            next_expected_activity=HandlingActivity.EMPTY,
            unloaded_at_destination=record.unloaded_at_dest,
            routing_status=RoutingStatus(record.routing_status),
            calculated_at=record.calculated_at,
            last_event_id=record.last_event_id,
        ),
        itinerary=Itinerary(legs) if legs else Itinerary.EMPTY,
        origin=_domain_location(record.origin),
    )


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_state_matches_its_handling_history(tmp_path):
    _load_fixture(tmp_path)

    for record in CargoRecord.objects.all():
        cargo = _domain_cargo(record)
        events = [
            _handling_event(event, cargo)
            for event in HandlingEventRecord.objects.filter(cargo=record)
        ]
        history = HandlingHistory(events, [event.id for event in events])
        derived = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            calculated_at=record.calculated_at,
        )

        assert record.transport_status == derived.transport_status.value
        assert record.misdirected == derived.misdirected
        assert record.unloaded_at_dest == derived.unloaded_at_destination
        assert record.routing_status == derived.routing_status.value
        assert record.last_event_id == history.most_recent_event_id
        if derived.last_known_location is None:
            assert record.last_known_location_id is None
        else:
            assert record.last_known_location.unlocode == derived.last_known_location.unlocode.value
        if derived.current_voyage is None:
            assert record.current_voyage_id is None
        else:
            assert (
                record.current_voyage.voyage_number
                == derived.current_voyage.voyage_number.value
            )
        if derived.eta is None:
            assert record.eta is None
        else:
            assert record.eta == derived.eta.date()
        activity = derived.next_expected_activity
        assert record.next_expected_handling_event_type == activity.event_type
        assert record.next_expected_location_id == (
            None
            if activity.location is None
            else LocationRecord.objects.get(unlocode=activity.location.unlocode.value).id
        )
        assert record.next_expected_voyage_id == (
            None
            if activity.voyage is None
            else VoyageRecord.objects.get(voyage_number=activity.voyage.voyage_number.value).id
        )


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(tmp_path):
    _load_fixture(tmp_path)

    for cargo_id in LegRecord.objects.values_list('cargo_id', flat=True).distinct():
        legs = list(LegRecord.objects.filter(cargo_id=cargo_id))
        assert all(
            previous.unload_location_id == following.load_location_id
            for previous, following in pairwise(legs)
        )


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_events_reference_existing_voyages_and_locations(tmp_path):
    _load_fixture(tmp_path)

    for event in HandlingEventRecord.objects.all():
        assert event.voyage_id is not None
        assert VoyageRecord.objects.filter(pk=event.voyage_id).exists()
        assert LocationRecord.objects.filter(pk=event.location_id).exists()


@pytest.mark.django_db(transaction=True)
def test_loaded_carrier_movement_schedules_are_ordered(tmp_path):
    _load_fixture(tmp_path)

    movements_by_voyage = defaultdict(list)
    for movement in CarrierMovementRecord.objects.order_by('voyage_id', 'departure_time'):
        assert movement.departure_time <= movement.arrival_time
        movements_by_voyage[movement.voyage_id].append(movement)

    for movements in movements_by_voyage.values():
        assert all(
            previous.arrival_time <= following.departure_time
            for previous, following in pairwise(movements)
        )
