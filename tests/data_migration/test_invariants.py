import csv
import hashlib
import json
import shutil
from dataclasses import replace
from itertools import pairwise
from pathlib import Path

import pytest
from django.core.management import call_command

from cargotracker.cargo.domain.delivery import Delivery
from cargotracker.cargo.infrastructure.models import CargoRecord
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.models import HandlingEventRecord
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.models import LocationRecord
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


def _valid_snapshot(tmp_path):
    snapshot = tmp_path / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)

    locations = _read_rows(snapshot, 'LOCATION')
    locations.append({'ID': '103', 'UNLOCODE': 'DEHAM', 'NAME': 'Hamburg'})
    _write_rows(snapshot, 'LOCATION', locations)

    voyages = _read_rows(snapshot, 'VOYAGE')
    voyages[0]['VOYAGE_NUMBER'] = 'V900'
    _write_rows(snapshot, 'VOYAGE', voyages)

    cargos = _read_rows(snapshot, 'CARGO')
    cargos[0].update(
        TRANSPORT_STATUS='ONBOARD_CARRIER',
        LAST_KNOWN_LOCATION_ID='101',
        CURRENT_VOYAGE_ID='900',
        MISDIRECTED='false',
        ETA='2026-11-10',
        NEXT_EXPECTED_HANDLING_EVENT_TYPE='UNLOAD',
        NEXT_EXPECTED_LOCATION_ID='103',
        NEXT_EXPECTED_VOYAGE_ID='900',
        UNLOADED_AT_DEST='false',
        ROUTING_STATUS='ROUTED',
    )
    _write_rows(snapshot, 'CARGO', cargos)

    handling_events = _read_rows(snapshot, 'HANDLINGEVENT')
    handling_events[0]['TYPE'] = 'LOAD'
    handling_events[0]['LOCATION_ID'] = '101'
    _write_rows(snapshot, 'HANDLINGEVENT', handling_events)

    legs = _read_rows(snapshot, 'LEG')
    legs[0].update(
        LOAD_TIME='2026-11-08T12:00:00Z',
        UNLOAD_TIME='2026-11-09T00:00:00Z',
        LOAD_LOCATION_ID='101',
        UNLOAD_LOCATION_ID='103',
    )
    legs.append(
        {
            **legs[0],
            'ID': '82',
            'LOAD_TIME': '2026-11-09T01:00:00Z',
            'UNLOAD_TIME': '2026-11-10T00:00:00Z',
            'LOAD_LOCATION_ID': '103',
            'UNLOAD_LOCATION_ID': '102',
        }
    )
    _write_rows(snapshot, 'LEG', legs)

    movements = _read_rows(snapshot, 'CARRIER_MOVEMENT')
    movements[0].update(
        ARRIVAL_TIME='2026-11-09T00:00:00Z',
        DEPARTURE_TIME='2026-11-08T12:00:00Z',
        ARRIVAL_LOCATION_ID='103',
        DEPARTURE_LOCATION_ID='101',
    )
    movements.append(
        {
            **movements[0],
            'ID': '92',
            'ARRIVAL_TIME': '2026-11-10T00:00:00Z',
            'DEPARTURE_TIME': '2026-11-09T01:00:00Z',
            'ARRIVAL_LOCATION_ID': '102',
            'DEPARTURE_LOCATION_ID': '103',
        }
    )
    _write_rows(snapshot, 'CARRIER_MOVEMENT', movements)

    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for table in ('LOCATION', 'VOYAGE', 'CARGO', 'HANDLINGEVENT', 'LEG', 'CARRIER_MOVEMENT'):
        path = snapshot / f'{table}.csv'
        manifest['tables'][table].update(
            rows=len(_read_rows(snapshot, table)),
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        )
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
    return snapshot


@pytest.fixture
def loaded_snapshot(tmp_path):
    snapshot = _valid_snapshot(tmp_path)
    call_command('load_data_snapshot', snapshot=str(snapshot), mapping=str(MAPPING))


@pytest.mark.django_db(transaction=True)
def test_cargo_delivery_state_matches_its_handling_history(loaded_snapshot):
    cargos = DjangoCargoRepository()
    handling_events = DjangoHandlingEventRepository()

    for cargo in cargos.find_all():
        history = handling_events.lookup_handling_history_of_cargo(cargo.tracking_id)
        derived_delivery = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            calculated_at=cargo.delivery.calculated_at,
        )

        assert replace(derived_delivery, last_event_id=history.most_recent_event_id) == (
            cargo.delivery
        )


@pytest.mark.django_db(transaction=True)
def test_each_cargo_itinerary_has_connected_legs(loaded_snapshot):
    for cargo in CargoRecord.objects.all():
        legs = list(cargo.legs.order_by('load_time', 'pk'))
        assert len(legs) >= 2
        assert all(
            previous.unload_location_id == following.load_location_id
            for previous, following in pairwise(legs)
        )


@pytest.mark.django_db(transaction=True)
def test_handling_events_reference_existing_voyages_and_locations(loaded_snapshot):
    location_ids = set(LocationRecord.objects.values_list('pk', flat=True))
    voyage_ids = set(VoyageRecord.objects.values_list('pk', flat=True))
    events = list(HandlingEventRecord.objects.all())

    assert events
    assert all(event.location_id in location_ids for event in events)
    assert all(event.voyage_id is None or event.voyage_id in voyage_ids for event in events)


@pytest.mark.django_db(transaction=True)
def test_each_voyage_carrier_movement_schedule_is_in_order(loaded_snapshot):
    assert CarrierMovementRecord.objects.count() >= 2

    for voyage in VoyageRecord.objects.all():
        movements = list(
            CarrierMovementRecord.objects.filter(voyage=voyage).order_by('departure_time', 'pk')
        )
        assert all(movement.departure_time <= movement.arrival_time for movement in movements)
        assert all(
            previous.arrival_time <= following.departure_time
            and previous.arrival_location_id == following.departure_location_id
            for previous, following in pairwise(movements)
        )
