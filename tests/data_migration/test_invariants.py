import csv
import hashlib
import json
import shutil
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

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = REPOSITORY_ROOT / '.migration' / 'data' / 'mapping.yaml'


def _read_table(snapshot, source):
    with (snapshot / f'{source}.csv').open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def _write_table(snapshot, source, fieldnames, rows, manifest):
    path = snapshot / f'{source}.csv'
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    manifest['tables'][source].update(
        rows=len(rows),
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
    )


def _load_snapshot(tmp_path):
    snapshot = tmp_path / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)
    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    tables = {
        source: _read_table(snapshot, source)
        for source in ('CARGO', 'CARRIER_MOVEMENT', 'HANDLINGEVENT', 'LEG', 'LOCATION')
    }

    fieldnames, cargos = tables['CARGO']
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
    _write_table(snapshot, 'CARGO', fieldnames, cargos, manifest)

    fieldnames, movements = tables['CARRIER_MOVEMENT']
    movements[0].update(
        DEPARTURE_TIME='2026-11-08T10:00:00Z',
        ARRIVAL_TIME='2026-11-09T10:00:00Z',
        DEPARTURE_LOCATION_ID='101',
        ARRIVAL_LOCATION_ID='102',
    )
    movements.append(
        {
            **movements[0],
            'ID': '92',
            'DEPARTURE_TIME': '2026-11-09T12:00:00Z',
            'ARRIVAL_TIME': '2026-11-10T14:00:00Z',
            'DEPARTURE_LOCATION_ID': '102',
            'ARRIVAL_LOCATION_ID': '103',
        }
    )
    _write_table(snapshot, 'CARRIER_MOVEMENT', fieldnames, movements, manifest)

    fieldnames, events = tables['HANDLINGEVENT']
    events[0].update(TYPE='RECEIVE', VOYAGE_ID='\\N', LOCATION_ID='101')
    events.append(
        {
            **events[0],
            'ID': '72',
            'TYPE': 'LOAD',
            'VOYAGE_ID': '900',
            'COMPLETIONTIME': '2026-11-07T11:00:00Z',
            'REGISTRATION': '2026-11-07T11:01:00Z',
        }
    )
    _write_table(snapshot, 'HANDLINGEVENT', fieldnames, events, manifest)

    fieldnames, legs = tables['LEG']
    legs[0].update(
        LOAD_TIME='2026-11-08T08:00:00Z',
        UNLOAD_TIME='2026-11-09T11:00:00Z',
        LOAD_LOCATION_ID='101',
        UNLOAD_LOCATION_ID='102',
    )
    legs.append(
        {
            **legs[0],
            'ID': '82',
            'LOAD_TIME': '2026-11-09T12:00:00Z',
            'UNLOAD_TIME': '2026-11-10T15:00:00Z',
            'LOAD_LOCATION_ID': '102',
            'UNLOAD_LOCATION_ID': '103',
        }
    )
    _write_table(snapshot, 'LEG', fieldnames, legs, manifest)

    fieldnames, locations = tables['LOCATION']
    locations.append({'ID': '103', 'UNLOCODE': 'SGSIN', 'NAME': 'Singapore'})
    _write_table(snapshot, 'LOCATION', fieldnames, locations, manifest)
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')

    call_command('load_data_snapshot', snapshot=str(snapshot), mapping=str(MAPPING))


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_matches_its_handling_history(tmp_path):
    _load_snapshot(tmp_path)
    cargo_repository = DjangoCargoRepository()
    event_repository = DjangoHandlingEventRepository()

    for cargo in cargo_repository.find_all():
        history = event_repository.lookup_handling_history_of_cargo(cargo.tracking_id)
        derived = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            calculated_at=cargo.delivery.calculated_at,
        )

        assert cargo.delivery.transport_status == derived.transport_status
        assert cargo.delivery.last_known_location == derived.last_known_location
        assert cargo.delivery.current_voyage == derived.current_voyage
        assert cargo.delivery.misdirected == derived.misdirected
        assert (
            cargo.delivery.eta.date() if cargo.delivery.eta else None
        ) == (derived.eta.date() if derived.eta else None)
        assert cargo.delivery.next_expected_activity == derived.next_expected_activity
        assert cargo.delivery.unloaded_at_destination == derived.unloaded_at_destination
        assert cargo.delivery.routing_status == derived.routing_status
        assert cargo.delivery.calculated_at == derived.calculated_at
        assert cargo.delivery.last_event_id == history.most_recent_event_id


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(tmp_path):
    _load_snapshot(tmp_path)

    for cargo in CargoRecord.objects.all():
        legs = list(cargo.legs.order_by('load_time', 'pk'))
        assert all(
            previous.unload_location_id == following.load_location_id
            for previous, following in zip(legs, legs[1:])
        )


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_events_reference_existing_voyages_and_locations(tmp_path):
    _load_snapshot(tmp_path)

    for event in HandlingEventRecord.objects.all():
        assert LocationRecord.objects.filter(pk=event.location_id).exists()
        if event.voyage_id is not None:
            assert VoyageRecord.objects.filter(pk=event.voyage_id).exists()


@pytest.mark.django_db(transaction=True)
def test_loaded_carrier_movement_schedules_are_in_order(tmp_path):
    _load_snapshot(tmp_path)
    for voyage in VoyageRecord.objects.all():
        movements = list(CarrierMovementRecord.objects.filter(voyage=voyage).order_by('pk'))
        movements = list(CarrierMovementRecord.objects.filter(voyage=voyage).order_by('pk'))
        assert all(movement.departure_time < movement.arrival_time for movement in movements)
        assert all(
            previous.arrival_time <= following.departure_time
            and previous.arrival_location_id == following.departure_location_id
            for previous, following in zip(movements, movements[1:])
        )
