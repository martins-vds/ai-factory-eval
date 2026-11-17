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
from cargotracker.cargo.infrastructure.models import CargoRecord, LegRecord
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
    with path.open(encoding='utf-8', newline='') as stream:
        columns = next(csv.reader(stream))
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def _leg(identifier, load_time, unload_time, load_location, unload_location):
    return {
        'ID': str(identifier),
        'LOAD_TIME': load_time,
        'UNLOAD_TIME': unload_time,
        'LOAD_LOCATION_ID': load_location,
        'UNLOAD_LOCATION_ID': unload_location,
        'VOYAGE_ID': '900',
        'CARGO_ID': '13',
    }


def _carrier_movement(identifier, departure_time, arrival_time, departure, arrival):
    return {
        'ID': str(identifier),
        'ARRIVAL_TIME': arrival_time,
        'DEPARTURE_TIME': departure_time,
        'ARRIVAL_LOCATION_ID': arrival,
        'DEPARTURE_LOCATION_ID': departure,
        'VOYAGE_ID': '900',
    }


def _valid_snapshot(tmp_path):
    snapshot = tmp_path / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)

    cargo = _read_rows(snapshot, 'CARGO')[0]
    cargo.update(
        TRANSPORT_STATUS='ONBOARD_CARRIER',
        LAST_KNOWN_LOCATION_ID='101',
        CURRENT_VOYAGE_ID='900',
        MISDIRECTED='false',
        ETA='2026-11-09',
        NEXT_EXPECTED_HANDLING_EVENT_TYPE='UNLOAD',
        NEXT_EXPECTED_LOCATION_ID='102',
        NEXT_EXPECTED_VOYAGE_ID='900',
        UNLOADED_AT_DEST='false',
        ROUTING_STATUS='ROUTED',
        CALCULATED_AT='2026-11-07T10:11:12Z',
        LAST_EVENT_ID='71',
    )
    _write_rows(snapshot, 'CARGO', [cargo])

    event = _read_rows(snapshot, 'HANDLINGEVENT')[0]
    event.update(
        TYPE='LOAD',
        VOYAGE_ID='900',
        LOCATION_ID='101',
        COMPLETIONTIME='2026-11-07T10:00:00Z',
        REGISTRATION='2026-11-07T10:01:00Z',
    )
    _write_rows(snapshot, 'HANDLINGEVENT', [event])

    legs = [
        _leg(81, '2026-11-08T08:00:00Z', '2026-11-08T12:00:00Z', '101', '102'),
        _leg(82, '2026-11-08T13:00:00Z', '2026-11-08T17:00:00Z', '102', '101'),
        _leg(83, '2026-11-08T18:00:00Z', '2026-11-09T00:00:00Z', '101', '102'),
    ]
    _write_rows(snapshot, 'LEG', legs)

    movements = [
        _carrier_movement(91, '2026-11-08T08:00:00Z', '2026-11-08T12:00:00Z', '101', '102'),
        _carrier_movement(92, '2026-11-08T13:00:00Z', '2026-11-08T17:00:00Z', '102', '101'),
        _carrier_movement(93, '2026-11-08T18:00:00Z', '2026-11-09T00:00:00Z', '101', '102'),
    ]
    _write_rows(snapshot, 'CARRIER_MOVEMENT', movements)

    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for table in ('CARGO', 'HANDLINGEVENT', 'LEG', 'CARRIER_MOVEMENT'):
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
def test_loaded_cargo_delivery_matches_its_handling_history(loaded_snapshot):
    cargos = DjangoCargoRepository()
    events = DjangoHandlingEventRepository()

    records = list(CargoRecord.objects.all())
    assert records
    for record in records:
        cargo = cargos.find(TrackingId(record.tracking_id))
        assert cargo is not None
        history = events.lookup_handling_history_of_cargo(cargo.tracking_id)
        assert history.most_recent_event is not None
        assert history.most_recent_event_id is not None

        derived = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            cargo.delivery.calculated_at,
        )
        assert replace(derived, last_event_id=history.most_recent_event_id) == cargo.delivery


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(loaded_snapshot):
    cargos = list(CargoRecord.objects.all())
    assert cargos

    for cargo in cargos:
        legs = list(LegRecord.objects.filter(cargo=cargo).order_by('load_time'))
        assert legs
        for previous, following in pairwise(legs):
            assert previous.unload_location_id == following.load_location_id


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_events_reference_existing_voyages_and_locations(loaded_snapshot):
    events = list(HandlingEventRecord.objects.all())
    assert events

    for event in events:
        assert LocationRecord.objects.filter(pk=event.location_id).exists()
        if event.voyage_id is not None:
            assert VoyageRecord.objects.filter(pk=event.voyage_id).exists()


@pytest.mark.django_db(transaction=True)
def test_loaded_carrier_movement_schedules_are_in_order(loaded_snapshot):
    voyage_ids = CarrierMovementRecord.objects.values_list('voyage_id', flat=True).distinct()
    assert voyage_ids

    for voyage_id in voyage_ids:
        movements = list(
            CarrierMovementRecord.objects.filter(voyage_id=voyage_id).order_by(
                'departure_time', 'pk'
            )
        )
        assert movements
        for movement in movements:
            assert movement.departure_time <= movement.arrival_time
        for previous, following in pairwise(movements):
            assert previous.arrival_time <= following.departure_time
            assert previous.arrival_location_id == following.departure_location_id
