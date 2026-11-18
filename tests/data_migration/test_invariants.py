import csv
import hashlib
import itertools
import json
import shutil
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

FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = Path(__file__).resolve().parents[2] / '.migration' / 'data' / 'mapping.yaml'


def _update_table(snapshot, table, updates, extra_rows=()):
    path = snapshot / f'{table}.csv'
    with path.open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        fieldnames = reader.fieldnames
        rows = list(reader)

    for row in rows:
        row.update(updates.get(row['ID'], {}))
    rows.extend(extra_rows)

    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest['tables'][table].update(
        rows=len(rows),
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
    )
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')


def _valid_snapshot(tmp_path):
    snapshot = tmp_path / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)

    _update_table(
        snapshot,
        'LOCATION',
        {},
        [{'ID': '103', 'UNLOCODE': 'JPTYO', 'NAME': 'Tokyo'}],
    )
    _update_table(
        snapshot,
        'CARGO',
        {
            '13': {
                'SPEC_DESTINATION_ID': '103',
                'TRANSPORT_STATUS': 'ONBOARD_CARRIER',
                'LAST_KNOWN_LOCATION_ID': '101',
                'CURRENT_VOYAGE_ID': '900',
                'MISDIRECTED': 'false',
                'ETA': '2026-11-13',
                'NEXT_EXPECTED_HANDLING_EVENT_TYPE': 'UNLOAD',
                'NEXT_EXPECTED_LOCATION_ID': '102',
                'NEXT_EXPECTED_VOYAGE_ID': '900',
                'UNLOADED_AT_DEST': 'false',
                'ROUTING_STATUS': 'ROUTED',
                'LAST_EVENT_ID': '72',
            }
        },
    )
    _update_table(
        snapshot,
        'HANDLINGEVENT',
        {
            '71': {
                'LOCATION_ID': '101',
                'VOYAGE_ID': r'\N',
                'COMPLETIONTIME': '2026-11-07T10:12:13Z',
                'REGISTRATION': '2026-11-07T10:13:14Z',
            }
        },
        [
            {
                'ID': '72',
                'TYPE': 'LOAD',
                'VOYAGE_ID': '900',
                'LOCATION_ID': '101',
                'COMPLETIONTIME': '2026-11-08T11:15:00Z',
                'REGISTRATION': '2026-11-08T11:16:00Z',
                'CARGO_ID': '13',
            }
        ],
    )
    _update_table(
        snapshot,
        'LEG',
        {
            '81': {
                'LOAD_TIME': '2026-11-08T11:00:00Z',
                'UNLOAD_TIME': '2026-11-09T11:00:00Z',
                'LOAD_LOCATION_ID': '101',
                'UNLOAD_LOCATION_ID': '102',
            }
        },
        [
            {
                'ID': '82',
                'LOAD_TIME': '2026-11-10T11:00:00Z',
                'UNLOAD_TIME': '2026-11-13T11:00:00Z',
                'LOAD_LOCATION_ID': '102',
                'UNLOAD_LOCATION_ID': '103',
                'VOYAGE_ID': '900',
                'CARGO_ID': '13',
            }
        ],
    )
    _update_table(
        snapshot,
        'CARRIER_MOVEMENT',
        {
            '91': {
                'DEPARTURE_TIME': '2026-11-08T12:00:00Z',
                'ARRIVAL_TIME': '2026-11-09T12:00:00Z',
                'DEPARTURE_LOCATION_ID': '101',
                'ARRIVAL_LOCATION_ID': '102',
            }
        },
        [
            {
                'ID': '92',
                'DEPARTURE_TIME': '2026-11-10T12:00:00Z',
                'ARRIVAL_TIME': '2026-11-13T12:00:00Z',
                'DEPARTURE_LOCATION_ID': '102',
                'ARRIVAL_LOCATION_ID': '103',
                'VOYAGE_ID': '900',
            }
        ],
    )
    return snapshot


@pytest.fixture
def loaded_snapshot(tmp_path):
    snapshot = _valid_snapshot(tmp_path)
    call_command(
        'load_data_snapshot',
        snapshot=str(snapshot),
        mapping=str(MAPPING),
    )


def _location_id(location):
    if location is None:
        return None
    return LocationRecord.objects.get(unlocode=location.unlocode.value).pk


def _voyage_id(voyage):
    if voyage is None:
        return None
    return VoyageRecord.objects.get(voyage_number=voyage.voyage_number.value).pk


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_matches_its_handling_history(loaded_snapshot):
    cargo_repository = DjangoCargoRepository()
    event_repository = DjangoHandlingEventRepository()

    for record in CargoRecord.objects.all():
        cargo = cargo_repository.find(TrackingId(record.tracking_id))
        history = event_repository.lookup_handling_history_of_cargo(cargo.tracking_id)
        derived = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            calculated_at=cargo.delivery.calculated_at,
        )
        activity = derived.next_expected_activity

        assert record.transport_status == derived.transport_status.value
        assert record.last_known_location_id == _location_id(derived.last_known_location)
        assert record.current_voyage_id == _voyage_id(derived.current_voyage)
        assert record.misdirected == derived.misdirected
        assert record.eta == (derived.eta.date() if derived.eta is not None else None)
        assert record.next_expected_handling_event_type == activity.event_type
        assert record.next_expected_location_id == _location_id(activity.location)
        assert record.next_expected_voyage_id == _voyage_id(activity.voyage)
        assert record.unloaded_at_dest == derived.unloaded_at_destination
        assert record.routing_status == derived.routing_status.value
        assert record.last_event_id == history.most_recent_event_id


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect_in_order(loaded_snapshot):
    for cargo in CargoRecord.objects.all():
        legs = list(LegRecord.objects.filter(cargo=cargo).order_by('load_time', 'pk'))
        assert legs
        for previous, following in itertools.pairwise(legs):
            assert previous.unload_location_id == following.load_location_id


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_events_reference_existing_cargo_voyages_and_locations(loaded_snapshot):
    events = list(HandlingEventRecord.objects.all())
    assert events
    assert any(event.voyage_id is not None for event in events)

    for event in events:
        assert CargoRecord.objects.filter(pk=event.cargo_id).exists()
        assert LocationRecord.objects.filter(pk=event.location_id).exists()
        if event.voyage_id is not None:
            assert VoyageRecord.objects.filter(pk=event.voyage_id).exists()


@pytest.mark.django_db(transaction=True)
def test_loaded_carrier_movement_schedules_are_in_order(loaded_snapshot):
    movements = list(CarrierMovementRecord.objects.all())
    assert len(movements) >= 2

    for voyage in VoyageRecord.objects.all():
        schedule = list(
            CarrierMovementRecord.objects.filter(voyage=voyage).order_by('departure_time', 'pk')
        )
        for movement in schedule:
            assert movement.departure_time <= movement.arrival_time
        for previous, following in itertools.pairwise(schedule):
            assert previous.arrival_time <= following.departure_time
            assert previous.arrival_location_id == following.departure_location_id
