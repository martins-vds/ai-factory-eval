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
from cargotracker.handling.infrastructure.models import HandlingEventRecord
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.models import LocationRecord
from cargotracker.voyage.infrastructure.models import CarrierMovementRecord, VoyageRecord

FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = Path(__file__).resolve().parents[2] / '.migration' / 'data' / 'mapping.yaml'

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def loaded_snapshot(tmp_path):
    snapshot = tmp_path / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)
    _make_delivery_consistent(snapshot)
    _refresh_manifest(snapshot)
    call_command(
        'load_data_snapshot',
        snapshot=str(snapshot),
        mapping=str(MAPPING),
    )


def _read_table(snapshot, table):
    with (snapshot / f'{table}.csv').open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def _write_table(snapshot, table, fieldnames, rows):
    with (snapshot / f'{table}.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _make_delivery_consistent(snapshot):
    fields, cargos = _read_table(snapshot, 'CARGO')
    cargo = cargos[0]
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
    cargos.append(
        {
            'ID': '14',
            'TRACKING_ID': 'FIDELITY-0002',
            'ORIGIN_ID': '101',
            'SPEC_ORIGIN_ID': '101',
            'SPEC_DESTINATION_ID': '103',
            'SPEC_ARRIVAL_DEADLINE': '2026-12-30',
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
            'CALCULATED_AT': '2026-11-07 10:11:12',
            'LAST_EVENT_ID': r'\N',
        }
    )
    _write_table(snapshot, 'CARGO', fields, cargos)

    fields, events = _read_table(snapshot, 'HANDLINGEVENT')
    events[0].update(TYPE='RECEIVE', VOYAGE_ID=r'\N', LOCATION_ID='101')
    events.append(
        {
            'ID': '72',
            'TYPE': 'LOAD',
            'VOYAGE_ID': '900',
            'LOCATION_ID': '101',
            'COMPLETIONTIME': '2026-11-08T06:00:00Z',
            'REGISTRATION': '2026-11-08T06:10:00Z',
            'CARGO_ID': '13',
        }
    )
    _write_table(snapshot, 'HANDLINGEVENT', fields, events)

    fields, legs = _read_table(snapshot, 'LEG')
    legs.append(
        {
            'ID': '82',
            'LOAD_TIME': '2026-11-10T12:00:00Z',
            'UNLOAD_TIME': '2026-11-11T14:00:00Z',
            'LOAD_LOCATION_ID': '102',
            'UNLOAD_LOCATION_ID': '103',
            'VOYAGE_ID': '901',
            'CARGO_ID': '13',
        }
    )
    _write_table(snapshot, 'LEG', fields, legs)

    fields, locations = _read_table(snapshot, 'LOCATION')
    locations.append({'ID': '103', 'UNLOCODE': 'FIHEL', 'NAME': 'Helsinki'})
    _write_table(snapshot, 'LOCATION', fields, locations)

    fields, voyages = _read_table(snapshot, 'VOYAGE')
    voyages[0]['VOYAGE_NUMBER'] = 'CM001'
    voyages.append({'ID': '901', 'VOYAGE_NUMBER': 'CM002'})
    _write_table(snapshot, 'VOYAGE', fields, voyages)

    fields, movements = _read_table(snapshot, 'CARRIER_MOVEMENT')
    movements[0].update(
        DEPARTURE_TIME='2026-11-08T08:00:00Z',
        ARRIVAL_TIME='2026-11-09T10:00:00Z',
    )
    movements.extend(
        (
            {
                'ID': '92',
                'DEPARTURE_TIME': '2026-11-10T12:00:00Z',
                'ARRIVAL_TIME': '2026-11-11T12:00:00Z',
                'DEPARTURE_LOCATION_ID': '102',
                'ARRIVAL_LOCATION_ID': '103',
                'VOYAGE_ID': '900',
            },
            {
                'ID': '93',
                'DEPARTURE_TIME': '2026-11-10T12:00:00Z',
                'ARRIVAL_TIME': '2026-11-11T14:00:00Z',
                'DEPARTURE_LOCATION_ID': '102',
                'ARRIVAL_LOCATION_ID': '103',
                'VOYAGE_ID': '901',
            },
        )
    )
    _write_table(snapshot, 'CARRIER_MOVEMENT', fields, movements)


def _refresh_manifest(snapshot):
    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for path in snapshot.glob('*.csv'):
        _, rows = _read_table(snapshot, path.stem)
        manifest['tables'][path.stem] = {
            'rows': len(rows),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')


def test_loaded_cargo_delivery_matches_its_handling_history(loaded_snapshot):
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
        if derived.eta is not None:
            derived = replace(
                derived, eta=derived.eta.replace(hour=0, minute=0, second=0, microsecond=0)
            )

        assert replace(derived, last_event_id=history.most_recent_event_id) == cargo.delivery


def test_loaded_itinerary_legs_connect(loaded_snapshot):
    cargos = DjangoCargoRepository().find_all()
    assert any(len(cargo.itinerary.legs) > 1 for cargo in cargos)

    for cargo in cargos:
        for first, following in pairwise(cargo.itinerary.legs):
            assert first.unload_location == following.load_location
            assert first.unload_time <= following.load_time


def test_loaded_handling_events_reference_existing_voyages_and_locations(loaded_snapshot):
    events = HandlingEventRecord.objects.all()
    assert events.exists()
    assert events.filter(voyage__isnull=False).exists()

    for event in events:
        assert LocationRecord.objects.filter(pk=event.location_id).exists()
        if event.voyage_id is not None:
            assert VoyageRecord.objects.filter(pk=event.voyage_id).exists()


def test_loaded_carrier_movement_schedules_are_in_order(loaded_snapshot):
    schedules = [
        list(CarrierMovementRecord.objects.filter(voyage=voyage).order_by('pk'))
        for voyage in VoyageRecord.objects.all()
    ]
    assert any(len(movements) > 1 for movements in schedules)

    for movements in schedules:
        assert movements == sorted(
            movements,
            key=lambda movement: (
                movement.departure_time,
                movement.arrival_time,
                movement.pk,
            ),
        )
        for movement in movements:
            assert movement.departure_time < movement.arrival_time
        for previous, following in pairwise(movements):
            assert previous.arrival_location_id == following.departure_location_id
            assert previous.arrival_time <= following.departure_time
