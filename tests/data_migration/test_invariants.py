import csv
import hashlib
import json
import shutil
from itertools import pairwise
from pathlib import Path

import pytest
from django.core.management import call_command

from cargotracker.cargo.infrastructure.models import CargoRecord, LegRecord
from cargotracker.handling.infrastructure.models import HandlingEventRecord
from cargotracker.location.infrastructure.models import LocationRecord
from cargotracker.voyage.infrastructure.models import CarrierMovementRecord, VoyageRecord

FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = Path(__file__).resolve().parents[2] / '.migration' / 'data' / 'mapping.yaml'


def _read_rows(snapshot, table):
    with (snapshot / f'{table}.csv').open(encoding='utf-8', newline='') as stream:
        return list(csv.DictReader(stream))


def _write_rows(snapshot, table, rows):
    path = snapshot / f'{table}.csv'
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest['tables'][table].update(
        rows=len(rows),
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
    )
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')


@pytest.fixture
def loaded_snapshot(tmp_path):
    snapshot = tmp_path / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)

    cargo_rows = _read_rows(snapshot, 'CARGO')
    cargo_rows[0]['TRANSPORT_STATUS'] = 'IN_PORT'
    _write_rows(snapshot, 'CARGO', cargo_rows)

    movements = _read_rows(snapshot, 'CARRIER_MOVEMENT')
    movements.append(
        {
            'ID': '92',
            'ARRIVAL_TIME': '2026-11-11T12:00:00Z',
            'DEPARTURE_TIME': '2026-11-10T12:00:00Z',
            'ARRIVAL_LOCATION_ID': '101',
            'DEPARTURE_LOCATION_ID': '102',
            'VOYAGE_ID': '900',
        }
    )
    _write_rows(snapshot, 'CARRIER_MOVEMENT', movements)

    call_command('load_data_snapshot', snapshot=str(snapshot), mapping=str(MAPPING))
    return snapshot


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_state_matches_its_handling_history(loaded_snapshot):
    expected_status = {
        'LOAD': 'ONBOARD_CARRIER',
        'UNLOAD': 'IN_PORT',
        'RECEIVE': 'IN_PORT',
        'CUSTOMS': 'IN_PORT',
        'CLAIM': 'CLAIMED',
    }

    for cargo in CargoRecord.objects.order_by('pk'):
        latest_event = (
            HandlingEventRecord.objects.filter(cargo_id=cargo.pk)
            .order_by('completion_time', 'registration_time', 'pk')
            .last()
        )
        status = (
            expected_status.get(latest_event.event_type, 'UNKNOWN')
            if latest_event
            else 'NOT_RECEIVED'
        )
        assert cargo.transport_status == status
        assert cargo.last_event_id == (latest_event.pk if latest_event else None)


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(loaded_snapshot):
    for cargo in CargoRecord.objects.order_by('pk'):
        legs = list(LegRecord.objects.filter(cargo_id=cargo.pk).order_by('load_time', 'pk'))
        if not legs:
            continue

        assert legs[0].load_location_id == cargo.spec_origin_id
        assert legs[-1].unload_location_id == cargo.spec_destination_id
        assert all(
            previous.unload_location_id == following.load_location_id
            for previous, following in pairwise(legs)
        )


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_events_reference_existing_voyages_and_locations(loaded_snapshot):
    assert HandlingEventRecord.objects.exists()

    for event in HandlingEventRecord.objects.all():
        assert event.voyage_id is not None
        assert VoyageRecord.objects.filter(pk=event.voyage_id).exists()
        assert event.location_id is not None
        assert LocationRecord.objects.filter(pk=event.location_id).exists()


@pytest.mark.django_db(transaction=True)
def test_loaded_voyage_schedules_are_in_order(loaded_snapshot):
    assert CarrierMovementRecord.objects.count() > 1

    for voyage in VoyageRecord.objects.order_by('pk'):
        movements = list(
            CarrierMovementRecord.objects.filter(voyage_id=voyage.pk).order_by(
                'departure_time', 'pk'
            )
        )
        assert all(movement.departure_time <= movement.arrival_time for movement in movements)
        assert all(
            previous.arrival_time <= following.departure_time
            for previous, following in pairwise(movements)
        )
