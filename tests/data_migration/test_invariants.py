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
from cargotracker.cargo.infrastructure.models import CargoRecord
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.models import HandlingEventRecord
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.models import LocationRecord
from cargotracker.voyage.infrastructure.models import CarrierMovementRecord, VoyageRecord

FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = Path(__file__).resolve().parents[2] / '.migration' / 'data' / 'mapping.yaml'


def _read_rows(path):
    with path.open(encoding='utf-8', newline='') as stream:
        return list(csv.DictReader(stream))


def _write_rows(path, rows):
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def _load_invariant_snapshot(tmp_path):
    snapshot = tmp_path / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)
    rows = {path.stem: _read_rows(path) for path in snapshot.glob('*.csv')}

    rows['LOCATION'].append({'ID': '103', 'UNLOCODE': 'DEHAM', 'NAME': 'Hamburg'})

    cargo = rows['CARGO'][0]
    cargo.update(
        {
            'TRANSPORT_STATUS': 'ONBOARD_CARRIER',
            'LAST_KNOWN_LOCATION_ID': '101',
            'CURRENT_VOYAGE_ID': '900',
            'MISDIRECTED': 'false',
            'ETA': '2026-11-11',
            'NEXT_EXPECTED_HANDLING_EVENT_TYPE': 'UNLOAD',
            'NEXT_EXPECTED_LOCATION_ID': '102',
            'NEXT_EXPECTED_VOYAGE_ID': '900',
            'UNLOADED_AT_DEST': 'false',
            'ROUTING_STATUS': 'ROUTED',
            'LAST_EVENT_ID': '72',
            'SPEC_DESTINATION_ID': '103',
        }
    )

    receive = rows['HANDLINGEVENT'][0]
    receive.update(
        {
            'TYPE': 'RECEIVE',
            'VOYAGE_ID': r'\N',
            'LOCATION_ID': '101',
            'COMPLETIONTIME': '2026-11-06T10:00:00Z',
            'REGISTRATION': '2026-11-06T10:01:00Z',
        }
    )
    load = receive.copy()
    load.update(
        {
            'ID': '72',
            'TYPE': 'LOAD',
            'VOYAGE_ID': '900',
            'COMPLETIONTIME': '2026-11-07T10:00:00Z',
            'REGISTRATION': '2026-11-07T10:01:00Z',
        }
    )
    rows['HANDLINGEVENT'].append(load)

    first_leg = rows['LEG'][0]
    first_leg.update(
        {
            'LOAD_TIME': '2026-11-08T08:00:00Z',
            'UNLOAD_TIME': '2026-11-09T11:00:00Z',
            'LOAD_LOCATION_ID': '101',
            'UNLOAD_LOCATION_ID': '102',
            'VOYAGE_ID': '900',
            'CARGO_ID': cargo['ID'],
        }
    )
    second_leg = first_leg.copy()
    second_leg.update(
        {
            'ID': '82',
            'LOAD_TIME': '2026-11-10T12:00:00Z',
            'UNLOAD_TIME': '2026-11-11T00:00:00Z',
            'LOAD_LOCATION_ID': '102',
            'UNLOAD_LOCATION_ID': '103',
        }
    )
    rows['LEG'].append(second_leg)

    first_movement = rows['CARRIER_MOVEMENT'][0]
    first_movement.update(
        {
            'ARRIVAL_TIME': '2026-11-09T10:00:00Z',
            'DEPARTURE_TIME': '2026-11-08T12:00:00Z',
            'ARRIVAL_LOCATION_ID': '102',
            'DEPARTURE_LOCATION_ID': '101',
            'VOYAGE_ID': '900',
        }
    )
    second_movement = first_movement.copy()
    second_movement.update(
        {
            'ID': '92',
            'ARRIVAL_TIME': '2026-11-10T23:00:00Z',
            'DEPARTURE_TIME': '2026-11-10T12:00:00Z',
            'ARRIVAL_LOCATION_ID': '103',
            'DEPARTURE_LOCATION_ID': '102',
        }
    )
    rows['CARRIER_MOVEMENT'].append(second_movement)

    for table, table_rows in rows.items():
        _write_rows(snapshot / f'{table}.csv', table_rows)

    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for table, table_rows in rows.items():
        path = snapshot / f'{table}.csv'
        manifest['tables'][table] = {
            'rows': len(table_rows),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
    call_command('load_data_snapshot', snapshot=str(snapshot), mapping=str(MAPPING))


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_matches_its_handling_history(tmp_path):
    _load_invariant_snapshot(tmp_path)
    cargo_repository = DjangoCargoRepository()
    handling_repository = DjangoHandlingEventRepository()
    cargos = CargoRecord.objects.all()
    assert cargos.exists()

    for record in cargos:
        cargo = cargo_repository.find(TrackingId(record.tracking_id))
        history = handling_repository.lookup_handling_history_of_cargo(cargo.tracking_id)
        derived_delivery = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            calculated_at=cargo.delivery.calculated_at,
        )
        derived_delivery = replace(derived_delivery, last_event_id=history.most_recent_event_id)

        assert cargo.delivery == derived_delivery


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(tmp_path):
    _load_invariant_snapshot(tmp_path)

    for cargo in CargoRecord.objects.all():
        legs = list(cargo.legs.order_by('load_time'))
        assert len(legs) > 1
        for current, following in pairwise(legs):
            assert current.unload_location_id == following.load_location_id


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_event_references_exist(tmp_path):
    _load_invariant_snapshot(tmp_path)
    events = HandlingEventRecord.objects.all()
    assert events.exists()

    for event in events:
        assert LocationRecord.objects.filter(pk=event.location_id).exists()
        if event.voyage_id is not None:
            assert VoyageRecord.objects.filter(pk=event.voyage_id).exists()


@pytest.mark.django_db(transaction=True)
def test_loaded_carrier_movement_schedules_are_ordered(tmp_path):
    _load_invariant_snapshot(tmp_path)
    voyage_ids = CarrierMovementRecord.objects.values_list('voyage_id', flat=True).distinct()
    voyages = VoyageRecord.objects.filter(pk__in=voyage_ids)
    assert voyages.exists()

    for voyage in voyages:
        movements = list(
            CarrierMovementRecord.objects.filter(voyage=voyage).order_by('departure_time')
        )
        assert len(movements) > 1
        for movement in movements:
            assert movement.departure_time <= movement.arrival_time
        for current, following in pairwise(movements):
            assert current.arrival_time <= following.departure_time
            assert current.arrival_location_id == following.departure_location_id
