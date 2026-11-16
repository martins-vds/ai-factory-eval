import csv
import hashlib
import json
import shutil
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

FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = Path(__file__).resolve().parents[2] / '.migration' / 'data' / 'mapping.yaml'


def _read_table(snapshot, table):
    with (snapshot / f'{table}.csv').open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def _write_table(snapshot, table, header, rows):
    path = snapshot / f'{table}.csv'
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


def _prepare_snapshot(directory):
    snapshot = directory / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)

    header, locations = _read_table(snapshot, 'LOCATION')
    locations.append({'ID': '103', 'UNLOCODE': 'GBSOU', 'NAME': 'Southampton'})
    _write_table(snapshot, 'LOCATION', header, locations)

    header, cargos = _read_table(snapshot, 'CARGO')
    cargos[0].update(
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
    _write_table(snapshot, 'CARGO', header, cargos)

    header, events = _read_table(snapshot, 'HANDLINGEVENT')
    events[0].update(VOYAGE_ID=r'\N', LOCATION_ID='101')
    events.append(
        {
            'ID': '72',
            'TYPE': 'LOAD',
            'VOYAGE_ID': '900',
            'LOCATION_ID': '101',
            'COMPLETIONTIME': '2026-11-08T09:00:00Z',
            'REGISTRATION': '2026-11-08T09:01:00Z',
            'CARGO_ID': '13',
        }
    )
    _write_table(snapshot, 'HANDLINGEVENT', header, events)

    header, legs = _read_table(snapshot, 'LEG')
    legs.append(
        {
            'ID': '82',
            'LOAD_TIME': '2026-11-10T12:00:00Z',
            'UNLOAD_TIME': '2026-11-11T00:00:00Z',
            'LOAD_LOCATION_ID': '102',
            'UNLOAD_LOCATION_ID': '103',
            'VOYAGE_ID': '900',
            'CARGO_ID': '13',
        }
    )
    _write_table(snapshot, 'LEG', header, legs)

    header, movements = _read_table(snapshot, 'CARRIER_MOVEMENT')
    movements.append(
        {
            'ID': '92',
            'ARRIVAL_TIME': '2026-11-11T00:00:00Z',
            'DEPARTURE_TIME': '2026-11-10T12:00:00Z',
            'ARRIVAL_LOCATION_ID': '103',
            'DEPARTURE_LOCATION_ID': '102',
            'VOYAGE_ID': '900',
        }
    )
    _write_table(snapshot, 'CARRIER_MOVEMENT', header, movements)

    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for table in ('LOCATION', 'CARGO', 'HANDLINGEVENT', 'LEG', 'CARRIER_MOVEMENT'):
        path = snapshot / f'{table}.csv'
        _, rows = _read_table(snapshot, table)
        manifest['tables'][table].update(
            rows=len(rows),
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        )
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')

    call_command(
        'load_data_snapshot',
        snapshot=str(snapshot),
        mapping=str(MAPPING),
    )


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_matches_its_handling_history(tmp_path):
    _prepare_snapshot(tmp_path)
    cargo_repository = DjangoCargoRepository()
    event_repository = DjangoHandlingEventRepository()

    records = CargoRecord.objects.order_by('pk')
    assert records.exists()
    for record in records:
        cargo = cargo_repository.find(TrackingId(record.tracking_id))
        history = event_repository.lookup_handling_history_of_cargo(cargo.tracking_id)
        derived_delivery = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            calculated_at=cargo.delivery.calculated_at,
        )

        assert history.most_recent_event is not None
        assert history.most_recent_event.event_type == 'LOAD'
        assert cargo.delivery.transport_status == 'ONBOARD_CARRIER'
        assert cargo.delivery == replace(
            derived_delivery,
            last_event_id=history.most_recent_event_id,
        )


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(tmp_path):
    _prepare_snapshot(tmp_path)
    cargos = DjangoCargoRepository().find_all()

    assert cargos
    assert any(len(cargo.itinerary.legs) > 1 for cargo in cargos)
    for cargo in cargos:
        for current, following in zip(cargo.itinerary.legs, cargo.itinerary.legs[1:]):
            assert current.unload_location == following.load_location


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_events_reference_existing_voyages_and_locations(tmp_path):
    _prepare_snapshot(tmp_path)
    events = list(HandlingEventRecord.objects.order_by('pk'))
    location_ids = set(LocationRecord.objects.values_list('pk', flat=True))
    voyage_ids = set(VoyageRecord.objects.values_list('pk', flat=True))

    assert events
    for event in events:
        assert event.location_id in location_ids
        if event.event_type in {'LOAD', 'UNLOAD'}:
            assert event.voyage_id is not None
        if event.voyage_id is not None:
            assert event.voyage_id in voyage_ids


@pytest.mark.django_db(transaction=True)
def test_loaded_voyage_carrier_movements_are_in_schedule_order(tmp_path):
    _prepare_snapshot(tmp_path)
    voyages = list(VoyageRecord.objects.order_by('pk'))
    schedules = [
        list(CarrierMovementRecord.objects.filter(voyage=voyage).order_by('departure_time'))
        for voyage in voyages
    ]

    assert any(len(movements) > 1 for movements in schedules)
    for movements in schedules:
        for movement in movements:
            assert movement.departure_time < movement.arrival_time
        for current, following in zip(movements, movements[1:]):
            assert current.arrival_time <= following.departure_time
            assert current.arrival_location_id == following.departure_location_id
