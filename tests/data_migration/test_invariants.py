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


def _write_snapshot(snapshot, tables):
    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for table, rows in tables.items():
        path = snapshot / f'{table}.csv'
        with path.open('w', encoding='utf-8', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=rows[0])
            writer.writeheader()
            writer.writerows(rows)
        manifest['tables'][table] = {
            'rows': len(rows),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')


def _load_invariant_snapshot(tmp_path):
    snapshot = tmp_path / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)
    tables = {
        table: _read_rows(snapshot, table)
        for table in (
            'CARGO',
            'CARRIER_MOVEMENT',
            'HANDLINGEVENT',
            'LEG',
            'LOCATION',
            'VOYAGE',
        )
    }

    tables['LOCATION'].extend(
        [
            {'ID': '103', 'UNLOCODE': 'USLAX', 'NAME': 'Los Angeles'},
        ]
    )
    cargo = tables['CARGO'][0]
    cargo.update(
        {
            'SPEC_DESTINATION_ID': '103',
            'TRANSPORT_STATUS': 'ONBOARD_CARRIER',
            'LAST_KNOWN_LOCATION_ID': '101',
            'CURRENT_VOYAGE_ID': '900',
            'MISDIRECTED': 'false',
            'ETA': '2026-11-10',
            'NEXT_EXPECTED_HANDLING_EVENT_TYPE': 'UNLOAD',
            'NEXT_EXPECTED_LOCATION_ID': '102',
            'NEXT_EXPECTED_VOYAGE_ID': '900',
            'UNLOADED_AT_DEST': 'false',
            'ROUTING_STATUS': 'ROUTED',
            'LAST_EVENT_ID': '72',
        }
    )
    tables['HANDLINGEVENT'][0].update({'VOYAGE_ID': r'\N', 'LOCATION_ID': '101'})
    tables['HANDLINGEVENT'].append(
        {
            'ID': '72',
            'TYPE': 'LOAD',
            'VOYAGE_ID': '900',
            'LOCATION_ID': '101',
            'COMPLETIONTIME': '2026-11-07T10:00:00Z',
            'REGISTRATION': '2026-11-07T10:01:00Z',
            'CARGO_ID': cargo['ID'],
        }
    )
    tables['LEG'].append(
        {
            'ID': '82',
            'LOAD_TIME': '2026-11-09T00:00:00Z',
            'UNLOAD_TIME': '2026-11-10T00:00:00Z',
            'LOAD_LOCATION_ID': '102',
            'UNLOAD_LOCATION_ID': '103',
            'VOYAGE_ID': '900',
            'CARGO_ID': cargo['ID'],
        }
    )
    tables['CARRIER_MOVEMENT'][0].update(
        {'DEPARTURE_LOCATION_ID': '101', 'ARRIVAL_LOCATION_ID': '102'}
    )
    tables['CARRIER_MOVEMENT'].append(
        {
            'ID': '92',
            'ARRIVAL_TIME': '2026-11-10T10:00:00Z',
            'DEPARTURE_TIME': '2026-11-09T10:00:00Z',
            'ARRIVAL_LOCATION_ID': '103',
            'DEPARTURE_LOCATION_ID': '102',
            'VOYAGE_ID': '900',
        }
    )
    _write_snapshot(snapshot, tables)
    call_command('load_data_snapshot', snapshot=str(snapshot), mapping=str(MAPPING))


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_matches_its_handling_history(tmp_path):
    _load_invariant_snapshot(tmp_path)
    cargo_repository = DjangoCargoRepository()
    history_repository = DjangoHandlingEventRepository()

    for record in CargoRecord.objects.all():
        cargo = cargo_repository.find(TrackingId(record.tracking_id))
        history = history_repository.lookup_handling_history_of_cargo(cargo.tracking_id)
        derived_delivery = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            calculated_at=cargo.delivery.calculated_at,
        )
        expected_delivery = replace(derived_delivery, last_event_id=history.most_recent_event_id)

        assert cargo.delivery == expected_delivery


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(tmp_path):
    _load_invariant_snapshot(tmp_path)

    itineraries = [list(cargo.legs.all()) for cargo in CargoRecord.objects.prefetch_related('legs')]

    assert all(itinerary for itinerary in itineraries)
    assert any(len(itinerary) > 1 for itinerary in itineraries)
    for itinerary in itineraries:
        for previous, following in zip(itinerary, itinerary[1:]):
            assert previous.unload_location_id == following.load_location_id


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_events_reference_existing_voyages_and_locations(tmp_path):
    _load_invariant_snapshot(tmp_path)
    events = HandlingEventRecord.objects.all()

    assert events.exists()
    for event in events:
        assert LocationRecord.objects.filter(pk=event.location_id).exists()
        if event.voyage_id is not None:
            assert VoyageRecord.objects.filter(pk=event.voyage_id).exists()


@pytest.mark.django_db(transaction=True)
def test_loaded_carrier_movement_schedules_are_in_order(tmp_path):
    _load_invariant_snapshot(tmp_path)
    voyages_with_schedules = 0

    for voyage in VoyageRecord.objects.all():
        movements = list(
            CarrierMovementRecord.objects.filter(voyage=voyage).order_by('departure_time', 'pk')
        )
        if movements:
            voyages_with_schedules += 1
        for movement in movements:
            assert movement.departure_time <= movement.arrival_time
        for previous, following in zip(movements, movements[1:]):
            assert previous.arrival_time <= following.departure_time

    assert voyages_with_schedules
    assert CarrierMovementRecord.objects.filter(voyage_id=900).count() > 1
