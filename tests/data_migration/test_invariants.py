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


def _read_table(snapshot, source):
    with (snapshot / f'{source}.csv').open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def _write_table(snapshot, source, fieldnames, rows):
    with (snapshot / f'{source}.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _snapshot_with_consistent_invariants(tmp_path):
    snapshot = tmp_path / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)

    fieldnames, rows = _read_table(snapshot, 'LOCATION')
    rows.append({'ID': '103', 'UNLOCODE': 'USCHI', 'NAME': 'Chicago'})
    _write_table(snapshot, 'LOCATION', fieldnames, rows)

    fieldnames, rows = _read_table(snapshot, 'CARGO')
    rows[0].update(
        SPEC_DESTINATION_ID='103',
        TRANSPORT_STATUS='ONBOARD_CARRIER',
        LAST_KNOWN_LOCATION_ID='101',
        CURRENT_VOYAGE_ID='900',
        MISDIRECTED='false',
        ETA='2026-11-11',
        NEXT_EXPECTED_HANDLING_EVENT_TYPE='UNLOAD',
        NEXT_EXPECTED_LOCATION_ID='102',
        NEXT_EXPECTED_VOYAGE_ID='900',
        ROUTING_STATUS='ROUTED',
        CALCULATED_AT='2026-11-07T10:11:12Z',
        LAST_EVENT_ID='72',
    )
    _write_table(snapshot, 'CARGO', fieldnames, rows)

    fieldnames, rows = _read_table(snapshot, 'VOYAGE')
    rows[0]['VOYAGE_NUMBER'] = '0100S'
    _write_table(snapshot, 'VOYAGE', fieldnames, rows)

    fieldnames, rows = _read_table(snapshot, 'HANDLINGEVENT')
    rows[0].update(
        TYPE='RECEIVE',
        VOYAGE_ID='\\N',
        LOCATION_ID='101',
        COMPLETIONTIME='2026-11-07T10:12:13Z',
        REGISTRATION='2026-11-07T10:13:14Z',
    )
    rows.append(
        {
            'ID': '72',
            'TYPE': 'LOAD',
            'VOYAGE_ID': '900',
            'LOCATION_ID': '101',
            'COMPLETIONTIME': '2026-11-08T00:00:00Z',
            'REGISTRATION': '2026-11-08T00:01:00Z',
            'CARGO_ID': '13',
        }
    )
    _write_table(snapshot, 'HANDLINGEVENT', fieldnames, rows)

    fieldnames, rows = _read_table(snapshot, 'LEG')
    rows[0].update(
        LOAD_TIME='2026-11-08T00:00:00Z',
        UNLOAD_TIME='2026-11-09T00:00:00Z',
        LOAD_LOCATION_ID='101',
        UNLOAD_LOCATION_ID='102',
    )
    rows.append(
        {
            'ID': '82',
            'LOAD_TIME': '2026-11-10T00:00:00Z',
            'UNLOAD_TIME': '2026-11-11T00:00:00Z',
            'LOAD_LOCATION_ID': '102',
            'UNLOAD_LOCATION_ID': '103',
            'VOYAGE_ID': '900',
            'CARGO_ID': '13',
        }
    )
    _write_table(snapshot, 'LEG', fieldnames, rows)

    fieldnames, rows = _read_table(snapshot, 'CARRIER_MOVEMENT')
    rows[0].update(
        ARRIVAL_TIME='2026-11-09T00:00:00Z',
        DEPARTURE_TIME='2026-11-08T00:00:00Z',
        ARRIVAL_LOCATION_ID='102',
        DEPARTURE_LOCATION_ID='101',
    )
    rows.append(
        {
            'ID': '92',
            'ARRIVAL_TIME': '2026-11-11T00:00:00Z',
            'DEPARTURE_TIME': '2026-11-10T00:00:00Z',
            'ARRIVAL_LOCATION_ID': '103',
            'DEPARTURE_LOCATION_ID': '102',
            'VOYAGE_ID': '900',
        }
    )
    _write_table(snapshot, 'CARRIER_MOVEMENT', fieldnames, rows)

    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for source in manifest['tables']:
        path = snapshot / f'{source}.csv'
        _, rows = _read_table(snapshot, source)
        manifest['tables'][source] = {
            'rows': len(rows),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
    return snapshot


@pytest.fixture
def loaded_snapshot(tmp_path):
    snapshot = _snapshot_with_consistent_invariants(tmp_path)
    call_command(
        'load_data_snapshot',
        snapshot=str(snapshot),
        mapping=str(MAPPING),
    )


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_matches_its_handling_history(loaded_snapshot):
    repository = DjangoCargoRepository()
    cargos = repository.find_all()
    assert cargos

    for cargo in cargos:
        history = DjangoHandlingEventRepository().lookup_handling_history_of_cargo(
            cargo.tracking_id
        )
        assert cargo.delivery.last_event_id == history.most_recent_event_id
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
    cargos = DjangoCargoRepository().find_all()
    assert cargos
    for cargo in cargos:
        assert len(cargo.itinerary.legs) == 2
        assert all(
            previous.unload_location == following.load_location
            for previous, following in zip(cargo.itinerary.legs, cargo.itinerary.legs[1:])
        )


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_event_references_exist(loaded_snapshot):
    location_ids = set(LocationRecord.objects.values_list('pk', flat=True))
    voyage_ids = set(VoyageRecord.objects.values_list('pk', flat=True))
    events = list(HandlingEventRecord.objects.all())

    assert events
    for event in events:
        assert event.location_id in location_ids
        if event.voyage_id is not None:
            assert event.voyage_id in voyage_ids


@pytest.mark.django_db(transaction=True)
def test_loaded_carrier_movements_are_in_schedule_order(loaded_snapshot):
    voyage = VoyageRecord.objects.get(voyage_number='0100S')
    movements = list(CarrierMovementRecord.objects.filter(voyage=voyage).order_by('pk'))

    assert len(movements) == 2
    assert [movement.departure_time for movement in movements] == sorted(
        movement.departure_time for movement in movements
    )
    for previous, following in pairwise(movements):
        assert previous.arrival_time <= following.departure_time
        assert previous.arrival_location_id == following.departure_location_id
