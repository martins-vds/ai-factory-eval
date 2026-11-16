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
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.domain.handling_event import HandlingEventType
from cargotracker.handling.infrastructure.models import HandlingEventRecord
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.models import LocationRecord
from cargotracker.voyage.infrastructure.models import CarrierMovementRecord, VoyageRecord

FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
PROJECT_ROOT = Path(__file__).resolve().parents[2]
MAPPING = PROJECT_ROOT / '.migration' / 'data' / 'mapping.yaml'


def _read_rows(snapshot, table):
    with (snapshot / f'{table}.csv').open(newline='', encoding='utf-8') as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def _write_rows(snapshot, table, fieldnames, rows):
    with (snapshot / f'{table}.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _make_invariant_snapshot(snapshot):
    headers, rows = _read_rows(snapshot, 'LOCATION')
    rows.append({'ID': '103', 'UNLOCODE': 'SGSIN', 'NAME': 'Singapore'})
    _write_rows(snapshot, 'LOCATION', headers, rows)

    headers, rows = _read_rows(snapshot, 'CARGO')
    rows[0].update(
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
        CALCULATED_AT='2026-11-08T12:06:00Z',
        LAST_EVENT_ID='72',
    )
    _write_rows(snapshot, 'CARGO', headers, rows)

    headers, rows = _read_rows(snapshot, 'HANDLINGEVENT')
    rows[0]['VOYAGE_ID'] = '\\N'
    rows.append(
        {
            'ID': '72',
            'TYPE': 'LOAD',
            'VOYAGE_ID': '900',
            'LOCATION_ID': '101',
            'COMPLETIONTIME': '2026-11-08T12:00:00Z',
            'REGISTRATION': '2026-11-08T12:05:00Z',
            'CARGO_ID': '13',
        }
    )
    _write_rows(snapshot, 'HANDLINGEVENT', headers, rows)

    headers, rows = _read_rows(snapshot, 'LEG')
    rows[0].update(
        LOAD_TIME='2026-11-08T12:00:00Z',
        UNLOAD_TIME='2026-11-09T12:00:00Z',
    )
    rows.append(
        {
            'ID': '82',
            'LOAD_TIME': '2026-11-09T12:00:00Z',
            'UNLOAD_TIME': '2026-11-10T00:00:00Z',
            'LOAD_LOCATION_ID': '102',
            'UNLOAD_LOCATION_ID': '103',
            'VOYAGE_ID': '900',
            'CARGO_ID': '13',
        }
    )
    _write_rows(snapshot, 'LEG', headers, rows)

    headers, rows = _read_rows(snapshot, 'CARRIER_MOVEMENT')
    rows[0]['ARRIVAL_TIME'] = '2026-11-09T12:00:00Z'
    rows.append(
        {
            'ID': '92',
            'ARRIVAL_TIME': '2026-11-10T00:00:00Z',
            'DEPARTURE_TIME': '2026-11-09T12:00:00Z',
            'ARRIVAL_LOCATION_ID': '103',
            'DEPARTURE_LOCATION_ID': '102',
            'VOYAGE_ID': '900',
        }
    )
    _write_rows(snapshot, 'CARRIER_MOVEMENT', headers, rows)

    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for table, metadata in manifest['tables'].items():
        path = snapshot / f'{table}.csv'
        with path.open(newline='', encoding='utf-8') as stream:
            metadata['rows'] = sum(1 for _ in csv.DictReader(stream))
        metadata['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')


def _load_fixture(tmp_path):
    snapshot = tmp_path / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)
    _make_invariant_snapshot(snapshot)
    call_command(
        'load_data_snapshot',
        snapshot=str(snapshot),
        mapping=str(MAPPING),
    )


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_matches_its_handling_history(tmp_path):
    _load_fixture(tmp_path)
    cargo_repository = DjangoCargoRepository()
    history_repository = DjangoHandlingEventRepository()

    cargo = cargo_repository.find(TrackingId('FIDELITY-0001'))
    history = history_repository.lookup_handling_history_of_cargo(cargo.tracking_id)
    derived_delivery = Delivery.derived_from(
        cargo.route_specification,
        cargo.itinerary,
        history,
        calculated_at=cargo.delivery.calculated_at,
    )

    assert replace(derived_delivery, last_event_id=history.most_recent_event_id) == cargo.delivery


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(tmp_path):
    _load_fixture(tmp_path)
    cargos = DjangoCargoRepository().find_all()

    assert any(len(cargo.itinerary.legs) > 1 for cargo in cargos)
    for cargo in cargos:
        for previous, following in pairwise(cargo.itinerary.legs):
            assert previous.unload_location == following.load_location
            assert previous.unload_time <= following.load_time


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_events_reference_existing_voyages_and_locations(tmp_path):
    _load_fixture(tmp_path)
    location_ids = set(LocationRecord.objects.values_list('pk', flat=True))
    voyage_ids = set(VoyageRecord.objects.values_list('pk', flat=True))
    events = list(HandlingEventRecord.objects.order_by('pk'))

    assert events
    for event in events:
        assert event.location_id in location_ids
        if event.event_type in (HandlingEventType.LOAD, HandlingEventType.UNLOAD):
            assert event.voyage_id in voyage_ids
        else:
            assert event.voyage_id is None


@pytest.mark.django_db(transaction=True)
def test_loaded_voyage_carrier_movements_are_contiguous_and_ordered(tmp_path):
    _load_fixture(tmp_path)
    voyages = list(VoyageRecord.objects.all())
    schedules = [
        list(CarrierMovementRecord.objects.filter(voyage=voyage).order_by('departure_time', 'pk'))
        for voyage in voyages
    ]

    assert any(len(schedule) > 1 for schedule in schedules)
    for schedule in schedules:
        for movement in schedule:
            assert movement.departure_time <= movement.arrival_time
        for previous, following in pairwise(schedule):
            assert previous.arrival_time <= following.departure_time
            assert previous.arrival_location_id == following.departure_location_id
