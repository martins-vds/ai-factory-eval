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
MAPPING = Path(__file__).parents[2] / '.migration' / 'data' / 'mapping.yaml'


def _read_rows(snapshot, table):
    with (snapshot / f'{table}.csv').open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def _write_rows(snapshot, table, header, rows):
    path = snapshot / f'{table}.csv'
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)

    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest['tables'][table].update(
        rows=len(rows),
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
    )
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')


def _loaded_snapshot(tmp_path):
    snapshot = tmp_path / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)

    location_header, locations = _read_rows(snapshot, 'LOCATION')
    locations.extend(
        [
            {
                **locations[0],
                'ID': '103',
                'UNLOCODE': 'SEGOT',
                'NAME': 'Gothenburg',
            },
            {
                **locations[0],
                'ID': '104',
                'UNLOCODE': 'FIHEL',
                'NAME': 'Helsinki',
            },
        ]
    )
    _write_rows(snapshot, 'LOCATION', location_header, locations)

    voyage_header, voyages = _read_rows(snapshot, 'VOYAGE')
    voyages[0]['VOYAGE_NUMBER'] = 'V001'
    voyages.append({**voyages[0], 'ID': '901', 'VOYAGE_NUMBER': 'V002'})
    _write_rows(snapshot, 'VOYAGE', voyage_header, voyages)

    cargo_header, cargos = _read_rows(snapshot, 'CARGO')
    cargo = cargos[0]
    cargo.update(
        {
            'ORIGIN_ID': '101',
            'SPEC_ORIGIN_ID': '101',
            'SPEC_DESTINATION_ID': '104',
            'SPEC_ARRIVAL_DEADLINE': '2026-12-30',
            'TRANSPORT_STATUS': 'IN_PORT',
            'LAST_KNOWN_LOCATION_ID': '103',
            'CURRENT_VOYAGE_ID': r'\N',
            'MISDIRECTED': 'false',
            'ETA': '2026-11-12',
            'NEXT_EXPECTED_HANDLING_EVENT_TYPE': 'LOAD',
            'NEXT_EXPECTED_LOCATION_ID': '103',
            'NEXT_EXPECTED_VOYAGE_ID': '901',
            'UNLOADED_AT_DEST': 'false',
            'ROUTING_STATUS': 'ROUTED',
            'CALCULATED_AT': '2026-11-15T02:35:59Z',
            'LAST_EVENT_ID': '73',
        }
    )
    cargos.append(
        {
            **cargo,
            'ID': '14',
            'TRACKING_ID': 'FIDELITY-NO-EVENT',
            'TRANSPORT_STATUS': 'NOT_RECEIVED',
            'LAST_KNOWN_LOCATION_ID': r'\N',
            'CURRENT_VOYAGE_ID': r'\N',
            'MISDIRECTED': 'false',
            'ETA': r'\N',
            'NEXT_EXPECTED_HANDLING_EVENT_TYPE': r'\N',
            'NEXT_EXPECTED_LOCATION_ID': r'\N',
            'NEXT_EXPECTED_VOYAGE_ID': r'\N',
            'UNLOADED_AT_DEST': 'false',
            'ROUTING_STATUS': 'NOT_ROUTED',
            'LAST_EVENT_ID': r'\N',
        }
    )
    _write_rows(snapshot, 'CARGO', cargo_header, cargos)

    event_header, events = _read_rows(snapshot, 'HANDLINGEVENT')
    receive = events[0]
    receive.update(
        {
            'TYPE': 'RECEIVE',
            'VOYAGE_ID': r'\N',
            'LOCATION_ID': '101',
            'COMPLETIONTIME': '2026-11-06T10:00:00Z',
            'REGISTRATION': '2026-11-06T10:01:00Z',
            'CARGO_ID': cargo['ID'],
        }
    )
    load = {
        **receive,
        'ID': '72',
        'TYPE': 'LOAD',
        'VOYAGE_ID': voyages[0]['ID'],
        'LOCATION_ID': '101',
        'COMPLETIONTIME': '2026-11-08T10:00:00Z',
        'REGISTRATION': '2026-11-08T10:01:00Z',
    }
    unload = {
        **receive,
        'ID': '73',
        'TYPE': 'UNLOAD',
        'VOYAGE_ID': voyages[0]['ID'],
        'LOCATION_ID': '103',
        'COMPLETIONTIME': '2026-11-10T10:00:00Z',
        'REGISTRATION': '2026-11-10T10:01:00Z',
    }
    _write_rows(snapshot, 'HANDLINGEVENT', event_header, [receive, load, unload])

    leg_header, legs = _read_rows(snapshot, 'LEG')
    first_leg = legs[0]
    first_leg.update(
        {
            'LOAD_TIME': '2026-11-08T10:00:00Z',
            'UNLOAD_TIME': '2026-11-10T10:00:00Z',
            'LOAD_LOCATION_ID': '101',
            'UNLOAD_LOCATION_ID': '103',
            'VOYAGE_ID': voyages[0]['ID'],
            'CARGO_ID': cargo['ID'],
        }
    )
    second_leg = {
        **first_leg,
        'ID': '82',
        'LOAD_TIME': '2026-11-11T10:00:00Z',
        'UNLOAD_TIME': '2026-11-12T00:00:00Z',
        'LOAD_LOCATION_ID': '103',
        'UNLOAD_LOCATION_ID': '104',
        'VOYAGE_ID': voyages[1]['ID'],
    }
    _write_rows(snapshot, 'LEG', leg_header, [first_leg, second_leg])

    movement_header, movements = _read_rows(snapshot, 'CARRIER_MOVEMENT')
    first_movement = movements[0]
    first_movement.update(
        {
            'ARRIVAL_TIME': '2026-11-09T10:00:00Z',
            'DEPARTURE_TIME': '2026-11-08T10:00:00Z',
            'ARRIVAL_LOCATION_ID': '102',
            'DEPARTURE_LOCATION_ID': '101',
            'VOYAGE_ID': voyages[0]['ID'],
        }
    )
    second_movement = {
        **first_movement,
        'ID': '92',
        'ARRIVAL_TIME': '2026-11-10T10:00:00Z',
        'DEPARTURE_TIME': '2026-11-09T12:00:00Z',
        'ARRIVAL_LOCATION_ID': '103',
        'DEPARTURE_LOCATION_ID': '102',
    }
    third_movement = {
        **first_movement,
        'ID': '93',
        'ARRIVAL_TIME': '2026-11-12T00:00:00Z',
        'DEPARTURE_TIME': '2026-11-11T10:00:00Z',
        'ARRIVAL_LOCATION_ID': '104',
        'DEPARTURE_LOCATION_ID': '103',
        'VOYAGE_ID': voyages[1]['ID'],
    }
    _write_rows(
        snapshot,
        'CARRIER_MOVEMENT',
        movement_header,
        [first_movement, second_movement, third_movement],
    )

    call_command(
        'load_data_snapshot',
        snapshot=str(snapshot),
        mapping=str(MAPPING),
    )
    return snapshot


@pytest.fixture
def loaded_snapshot(tmp_path):
    return _loaded_snapshot(tmp_path)


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_rederives_from_handling_history(loaded_snapshot):
    cargo_repository = DjangoCargoRepository()
    handling_event_repository = DjangoHandlingEventRepository()
    cargos = cargo_repository.find_all()

    assert len(cargos) == 2
    for cargo in cargos:
        history = handling_event_repository.lookup_handling_history_of_cargo(cargo.tracking_id)
        derived_delivery = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            calculated_at=cargo.delivery.calculated_at,
        )

        assert (
            replace(derived_delivery, last_event_id=history.most_recent_event_id) == cargo.delivery
        )


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(loaded_snapshot):
    cargo_legs = {
        cargo.pk: list(cargo.legs.order_by('load_time', 'pk'))
        for cargo in CargoRecord.objects.all()
    }

    assert len(cargo_legs[13]) == 2
    assert all(
        previous.unload_location_id == following.load_location_id
        for legs in cargo_legs.values()
        for previous, following in pairwise(legs)
    )


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_events_reference_existing_voyages_and_locations(loaded_snapshot):
    location_ids = set(LocationRecord.objects.values_list('pk', flat=True))
    voyage_ids = set(VoyageRecord.objects.values_list('pk', flat=True))
    events = list(HandlingEventRecord.objects.order_by('pk'))

    assert events
    for event in events:
        assert event.location_id in location_ids
        if event.event_type in {'LOAD', 'UNLOAD'}:
            assert event.voyage_id is not None
        if event.voyage_id is not None:
            assert event.voyage_id in voyage_ids


@pytest.mark.django_db(transaction=True)
def test_loaded_voyage_carrier_movements_are_chronological(loaded_snapshot):
    voyages = list(VoyageRecord.objects.order_by('pk'))

    assert len(voyages) == 2
    for voyage in voyages:
        movements = list(
            CarrierMovementRecord.objects.filter(voyage=voyage).order_by('departure_time', 'pk')
        )
        assert movements
        assert all(
            previous.arrival_time <= following.departure_time
            and previous.arrival_location_id == following.departure_location_id
            for previous, following in pairwise(movements)
        )
