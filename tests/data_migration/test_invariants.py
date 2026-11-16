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
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.domain.handling_event import HandlingEventType
from cargotracker.handling.infrastructure.models import HandlingEventRecord
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.models import LocationRecord
from cargotracker.voyage.infrastructure.models import CarrierMovementRecord, VoyageRecord

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = ROOT / '.migration' / 'data' / 'mapping.yaml'


def _read_table(snapshot, table):
    with (snapshot / f'{table}.csv').open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def _write_table(snapshot, table, headers, rows):
    with (snapshot / f'{table}.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def _invariant_snapshot(tmp_path):
    snapshot = tmp_path / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)

    headers, locations = _read_table(snapshot, 'LOCATION')
    locations.append({'ID': '103', 'UNLOCODE': 'USLAX', 'NAME': 'Los Angeles'})
    _write_table(snapshot, 'LOCATION', headers, locations)

    headers, voyages = _read_table(snapshot, 'VOYAGE')
    voyages[0]['VOYAGE_NUMBER'] = 'V001'
    _write_table(snapshot, 'VOYAGE', headers, voyages)

    headers, cargos = _read_table(snapshot, 'CARGO')
    cargos[0].update(
        SPEC_DESTINATION_ID='103',
        TRANSPORT_STATUS='ONBOARD_CARRIER',
        LAST_KNOWN_LOCATION_ID='101',
        CURRENT_VOYAGE_ID='900',
        MISDIRECTED='false',
        ETA='2026-11-10',
        NEXT_EXPECTED_HANDLING_EVENT_TYPE='UNLOAD',
        NEXT_EXPECTED_LOCATION_ID='102',
        NEXT_EXPECTED_VOYAGE_ID='900',
        UNLOADED_AT_DEST='false',
        ROUTING_STATUS='ROUTED',
        LAST_EVENT_ID='72',
    )
    _write_table(snapshot, 'CARGO', headers, cargos)

    headers, events = _read_table(snapshot, 'HANDLINGEVENT')
    events[0].update(VOYAGE_ID=r'\N', LOCATION_ID='101')
    load_event = events[0].copy()
    load_event.update(
        ID='72',
        TYPE='LOAD',
        VOYAGE_ID='900',
        COMPLETIONTIME='2026-11-08T10:30:00Z',
        REGISTRATION='2026-11-08T10:31:00Z',
    )
    events.append(load_event)
    _write_table(snapshot, 'HANDLINGEVENT', headers, events)

    headers, legs = _read_table(snapshot, 'LEG')
    legs[0].update(
        LOAD_TIME='2026-11-08T10:00:00Z',
        UNLOAD_TIME='2026-11-09T10:00:00Z',
        LOAD_LOCATION_ID='101',
        UNLOAD_LOCATION_ID='102',
    )
    second_leg = legs[0].copy()
    second_leg.update(
        ID='82',
        LOAD_TIME='2026-11-09T12:00:00Z',
        UNLOAD_TIME='2026-11-10T00:00:00Z',
        LOAD_LOCATION_ID='102',
        UNLOAD_LOCATION_ID='103',
    )
    legs.append(second_leg)
    _write_table(snapshot, 'LEG', headers, legs)

    headers, movements = _read_table(snapshot, 'CARRIER_MOVEMENT')
    movements[0].update(
        ARRIVAL_TIME='2026-11-09T10:00:00Z',
        DEPARTURE_TIME='2026-11-08T10:00:00Z',
        ARRIVAL_LOCATION_ID='102',
        DEPARTURE_LOCATION_ID='101',
    )
    second_movement = movements[0].copy()
    second_movement.update(
        ID='92',
        ARRIVAL_TIME='2026-11-10T00:00:00Z',
        DEPARTURE_TIME='2026-11-09T12:00:00Z',
        ARRIVAL_LOCATION_ID='103',
        DEPARTURE_LOCATION_ID='102',
    )
    movements.append(second_movement)
    _write_table(snapshot, 'CARRIER_MOVEMENT', headers, movements)

    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for path in snapshot.glob('*.csv'):
        with path.open(encoding='utf-8', newline='') as stream:
            row_count = sum(1 for _ in csv.DictReader(stream))
        manifest['tables'][path.stem].update(
            rows=row_count,
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        )
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
    return snapshot


def _load_snapshot(snapshot):
    call_command('load_data_snapshot', snapshot=str(snapshot), mapping=str(MAPPING))


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_matches_its_handling_history(tmp_path):
    _load_snapshot(_invariant_snapshot(tmp_path))

    cargo_repository = DjangoCargoRepository()
    handling_events = DjangoHandlingEventRepository()
    cargos = cargo_repository.find_all()
    assert cargos

    for cargo in cargos:
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
def test_loaded_itinerary_legs_connect(tmp_path):
    _load_snapshot(_invariant_snapshot(tmp_path))

    cargos = DjangoCargoRepository().find_all()
    assert cargos
    assert any(len(cargo.itinerary.legs) > 1 for cargo in cargos)

    for cargo in cargos:
        for previous, following in pairwise(cargo.itinerary.legs):
            assert previous.unload_location == following.load_location


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_events_reference_existing_voyages_and_locations(tmp_path):
    _load_snapshot(_invariant_snapshot(tmp_path))

    location_ids = set(LocationRecord.objects.values_list('pk', flat=True))
    voyage_ids = set(VoyageRecord.objects.values_list('pk', flat=True))
    events = list(HandlingEventRecord.objects.all())
    assert events
    assert any(event.voyage_id is None for event in events)
    assert any(event.voyage_id is not None for event in events)

    for event in events:
        assert event.location_id in location_ids
        if event.voyage_id is not None:
            assert event.voyage_id in voyage_ids
        if HandlingEventType(event.event_type).requires_voyage:
            assert event.voyage_id in voyage_ids


@pytest.mark.django_db(transaction=True)
def test_loaded_voyage_carrier_movements_are_in_schedule_order(tmp_path):
    _load_snapshot(_invariant_snapshot(tmp_path))

    voyages_with_movements = []
    for voyage in VoyageRecord.objects.all():
        movements = list(
            CarrierMovementRecord.objects.filter(voyage=voyage).order_by('departure_time', 'pk')
        )
        if len(movements) > 1:
            voyages_with_movements.append(movements)

        for previous, following in pairwise(movements):
            assert previous.arrival_location_id == following.departure_location_id
            assert previous.arrival_time <= following.departure_time

    assert voyages_with_movements
