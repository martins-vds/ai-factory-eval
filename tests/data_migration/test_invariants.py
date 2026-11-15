import csv
import hashlib
import json
import shutil
from itertools import pairwise
from pathlib import Path

import pytest
from django.core.management import call_command

from cargotracker.cargo.domain.delivery import Delivery
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.models import HandlingEventRecord
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.models import LocationRecord
from cargotracker.voyage.infrastructure.models import CarrierMovementRecord, VoyageRecord

FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = Path(__file__).resolve().parents[2] / '.migration' / 'data' / 'mapping.yaml'


def _read_table(snapshot, table):
    with (snapshot / f'{table}.csv').open(encoding='utf-8', newline='') as source:
        reader = csv.DictReader(source)
        return reader.fieldnames, list(reader)


def _write_tables(snapshot, tables):
    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for table, (fieldnames, rows) in tables.items():
        path = snapshot / f'{table}.csv'
        with path.open('w', encoding='utf-8', newline='') as target:
            writer = csv.DictWriter(target, fieldnames=fieldnames, lineterminator='\n')
            writer.writeheader()
            writer.writerows(rows)
        manifest['tables'][table] = {
            'rows': len(rows),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')


def _consistent_snapshot(snapshot):
    tables = {
        table: _read_table(snapshot, table)
        for table in ('CARGO', 'CARRIER_MOVEMENT', 'HANDLINGEVENT', 'LEG', 'LOCATION')
    }
    cargo = tables['CARGO'][1][0]
    cargo.update(
        SPEC_DESTINATION_ID='103',
        TRANSPORT_STATUS='ONBOARD_CARRIER',
        LAST_KNOWN_LOCATION_ID='101',
        CURRENT_VOYAGE_ID='900',
        MISDIRECTED='false',
        ETA='2026-11-11',
        NEXT_EXPECTED_HANDLING_EVENT_TYPE='UNLOAD',
        NEXT_EXPECTED_LOCATION_ID='102',
        NEXT_EXPECTED_VOYAGE_ID='900',
        UNLOADED_AT_DEST='false',
        ROUTING_STATUS='ROUTED',
        LAST_EVENT_ID='72',
    )
    event = tables['HANDLINGEVENT'][1][0]
    event.update(
        VOYAGE_ID=r'\N',
        LOCATION_ID='101',
        COMPLETIONTIME='2026-11-07T10:12:13Z',
        REGISTRATION='2026-11-07T10:13:14Z',
    )
    tables['HANDLINGEVENT'][1].append(
        {
            'ID': '72',
            'TYPE': 'LOAD',
            'VOYAGE_ID': '900',
            'LOCATION_ID': '101',
            'COMPLETIONTIME': '2026-11-08T12:00:00Z',
            'REGISTRATION': '2026-11-08T12:01:00Z',
            'CARGO_ID': '13',
        }
    )
    tables['LOCATION'][1].append({'ID': '103', 'UNLOCODE': 'JPTYO', 'NAME': 'Tokyo'})
    tables['LEG'][1][0].update(
        LOAD_TIME='2026-11-08T12:00:00Z',
        UNLOAD_TIME='2026-11-09T12:00:00Z',
        LOAD_LOCATION_ID='101',
        UNLOAD_LOCATION_ID='102',
    )
    tables['LEG'][1].append(
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
    tables['CARRIER_MOVEMENT'][1][0].update(
        ARRIVAL_TIME='2026-11-09T12:00:00Z',
        DEPARTURE_TIME='2026-11-08T12:00:00Z',
        ARRIVAL_LOCATION_ID='102',
        DEPARTURE_LOCATION_ID='101',
    )
    tables['CARRIER_MOVEMENT'][1].append(
        {
            'ID': '92',
            'ARRIVAL_TIME': '2026-11-11T12:00:00Z',
            'DEPARTURE_TIME': '2026-11-10T12:00:00Z',
            'ARRIVAL_LOCATION_ID': '103',
            'DEPARTURE_LOCATION_ID': '102',
            'VOYAGE_ID': '900',
        }
    )
    tables['CARRIER_MOVEMENT'][1].reverse()
    _write_tables(snapshot, tables)


@pytest.fixture
def loaded_snapshot(tmp_path):
    snapshot = tmp_path / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)
    _consistent_snapshot(snapshot)
    call_command('load_data_snapshot', snapshot=str(snapshot), mapping=str(MAPPING))


def _delivery_state(delivery):
    return (
        delivery.transport_status,
        delivery.last_known_location,
        delivery.current_voyage,
        delivery.misdirected,
        delivery.eta.date() if delivery.eta is not None else None,
        delivery.next_expected_activity,
        delivery.unloaded_at_destination,
        delivery.routing_status,
    )


@pytest.mark.django_db
def test_loaded_cargo_delivery_state_matches_its_handling_history(loaded_snapshot):
    repository = DjangoCargoRepository()
    history_repository = DjangoHandlingEventRepository()
    cargos = repository.find_all()
    assert cargos

    for cargo in cargos:
        history = history_repository.lookup_handling_history_of_cargo(cargo.tracking_id)
        derived = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            cargo.delivery.calculated_at,
        )

        assert _delivery_state(derived) == _delivery_state(cargo.delivery)
        assert cargo.delivery.last_event_id == history.most_recent_event_id


@pytest.mark.django_db
def test_loaded_itinerary_legs_connect(loaded_snapshot):
    cargos = DjangoCargoRepository().find_all()
    assert cargos
    assert any(len(cargo.itinerary.legs) >= 2 for cargo in cargos)

    for cargo in cargos:
        legs = list(cargo.itinerary.legs)
        assert all(
            previous.unload_location == following.load_location
            for previous, following in pairwise(legs)
        )


@pytest.mark.django_db
def test_loaded_handling_events_reference_existing_voyages_and_locations(loaded_snapshot):
    events = list(HandlingEventRecord.objects.all())
    assert events
    assert any(event.voyage_id is not None for event in events)

    for event in events:
        assert event.location_id is not None
        assert LocationRecord.objects.filter(pk=event.location_id).exists()
        if event.voyage_id is not None:
            assert VoyageRecord.objects.filter(pk=event.voyage_id).exists()


@pytest.mark.django_db
def test_loaded_carrier_movement_schedules_are_in_order(loaded_snapshot):
    voyages = VoyageRecord.objects.all()
    assert voyages.exists()
    schedules = []

    for voyage in voyages:
        movements = list(
            CarrierMovementRecord.objects.filter(voyage=voyage).order_by('departure_time', 'pk')
        )
        for movement in movements:
            assert movement.departure_time < movement.arrival_time
        for previous, following in pairwise(movements):
            assert previous.arrival_time <= following.departure_time
            assert previous.arrival_location_id == following.departure_location_id
        schedules.append(movements)

    assert any(len(schedule) >= 2 for schedule in schedules)
