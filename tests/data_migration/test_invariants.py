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
PROJECT_ROOT = Path(__file__).resolve().parents[2]
MAPPING = PROJECT_ROOT / '.migration' / 'data' / 'mapping.yaml'


def _rewrite_table(snapshot, table, update_rows):
    path = snapshot / f'{table}.csv'
    with path.open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        fieldnames = reader.fieldnames
        rows = list(reader)
    update_rows(rows)

    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)

    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest['tables'][table] = {
        'rows': len(rows),
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
    }
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')


def _make_invariant_snapshot(tmp_path):
    snapshot = tmp_path / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)

    def add_destination(rows):
        rows.append({'ID': '103', 'UNLOCODE': 'BEANR', 'NAME': 'Antwerp'})

    _rewrite_table(snapshot, 'LOCATION', add_destination)
    _rewrite_table(
        snapshot,
        'VOYAGE',
        lambda rows: rows[0].update(VOYAGE_NUMBER='V001'),
    )
    _rewrite_table(
        snapshot,
        'CARGO',
        lambda rows: rows[0].update(
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
        ),
    )

    def add_load_event(rows):
        rows[0].update(VOYAGE_ID='\\N', LOCATION_ID='101')
        rows.append(
            {
                'ID': '72',
                'TYPE': 'LOAD',
                'VOYAGE_ID': '900',
                'LOCATION_ID': '101',
                'COMPLETIONTIME': '2026-11-08T12:00:00Z',
                'REGISTRATION': '2026-11-08T12:01:00Z',
                'CARGO_ID': '13',
            }
        )

    _rewrite_table(snapshot, 'HANDLINGEVENT', add_load_event)

    def add_second_leg(rows):
        rows[0].update(
            LOAD_TIME='2026-11-08T12:00:00Z',
            UNLOAD_TIME='2026-11-09T10:00:00Z',
        )
        rows.append(
            {
                'ID': '82',
                'LOAD_TIME': '2026-11-09T12:00:00Z',
                'UNLOAD_TIME': '2026-11-10T10:00:00Z',
                'LOAD_LOCATION_ID': '102',
                'UNLOAD_LOCATION_ID': '103',
                'VOYAGE_ID': '900',
                'CARGO_ID': '13',
            }
        )

    _rewrite_table(snapshot, 'LEG', add_second_leg)

    def add_second_movement(rows):
        rows.append(
            {
                'ID': '92',
                'ARRIVAL_TIME': '2026-11-10T10:00:00Z',
                'DEPARTURE_TIME': '2026-11-09T12:00:00Z',
                'ARRIVAL_LOCATION_ID': '103',
                'DEPARTURE_LOCATION_ID': '102',
                'VOYAGE_ID': '900',
            }
        )

    _rewrite_table(snapshot, 'CARRIER_MOVEMENT', add_second_movement)
    return snapshot


@pytest.fixture
def loaded_snapshot(tmp_path):
    snapshot = _make_invariant_snapshot(tmp_path)
    call_command(
        'load_data_snapshot',
        snapshot=str(snapshot),
        mapping=str(MAPPING),
    )


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_matches_its_route_and_handling_history(loaded_snapshot):
    cargo_repository = DjangoCargoRepository()
    event_repository = DjangoHandlingEventRepository()

    for record in CargoRecord.objects.all():
        cargo = cargo_repository.find(TrackingId(record.tracking_id))
        history = event_repository.lookup_handling_history_of_cargo(cargo.tracking_id)
        derived = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            calculated_at=cargo.delivery.calculated_at,
        )
        expected = replace(
            derived,
            eta=(
                derived.eta.replace(hour=0, minute=0, second=0, microsecond=0)
                if derived.eta is not None
                else None
            ),
            last_event_id=history.most_recent_event_id,
        )

        assert cargo.delivery == expected


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(loaded_snapshot):
    for cargo in CargoRecord.objects.prefetch_related('legs').all():
        legs = list(cargo.legs.all())
        if not legs:
            continue

        assert legs[0].load_location_id == cargo.spec_origin_id
        assert legs[-1].unload_location_id == cargo.spec_destination_id
        for previous, following in pairwise(legs):
            assert previous.unload_location_id == following.load_location_id
            assert previous.unload_time <= following.load_time


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_events_reference_existing_voyages_and_locations(loaded_snapshot):
    for event in HandlingEventRecord.objects.all():
        assert LocationRecord.objects.filter(pk=event.location_id).exists()
        assert event.voyage_id is None or VoyageRecord.objects.filter(pk=event.voyage_id).exists()


@pytest.mark.django_db(transaction=True)
def test_loaded_carrier_movement_schedules_are_ordered(loaded_snapshot):
    for voyage in VoyageRecord.objects.all():
        movements = list(
            CarrierMovementRecord.objects.filter(voyage=voyage).order_by('departure_time', 'pk')
        )
        for movement in movements:
            assert movement.departure_time < movement.arrival_time
        for previous, following in pairwise(movements):
            assert previous.arrival_location_id == following.departure_location_id
            assert previous.arrival_time <= following.departure_time
