import csv
import hashlib
import itertools
import json
import shutil
from dataclasses import replace
from pathlib import Path

import pytest
from django.core.management import call_command

from cargotracker.cargo.domain.delivery import Delivery
from cargotracker.cargo.infrastructure.models import CargoRecord, LegRecord
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.models import HandlingEventRecord
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.models import LocationRecord
from cargotracker.voyage.infrastructure.models import CarrierMovementRecord, VoyageRecord

SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = Path(__file__).resolve().parents[2] / '.migration' / 'data' / 'mapping.yaml'


def _rewrite_table(snapshot, table, update_rows, additions=()):
    path = snapshot / f'{table}.csv'
    with path.open(encoding='utf-8', newline='') as source:
        reader = csv.DictReader(source)
        columns = reader.fieldnames
        rows = update_rows(list(reader))
    rows.extend(additions)
    with path.open('w', encoding='utf-8', newline='') as target:
        writer = csv.DictWriter(target, fieldnames=columns)
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
    shutil.copytree(SNAPSHOT, snapshot)

    def update_cargo(rows):
        rows[0].update(
            ORIGIN_ID='101',
            SPEC_ORIGIN_ID='101',
            SPEC_DESTINATION_ID='103',
            SPEC_ARRIVAL_DEADLINE='2026-12-30',
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
        return rows

    _rewrite_table(
        snapshot,
        'LOCATION',
        lambda rows: rows,
        [{'ID': '103', 'UNLOCODE': 'USLAX', 'NAME': 'Los Angeles'}],
    )
    _rewrite_table(snapshot, 'CARGO', update_cargo)
    _rewrite_table(
        snapshot,
        'HANDLINGEVENT',
        lambda rows: [
            {
                **rows[0],
                'VOYAGE_ID': r'\N',
                'LOCATION_ID': '101',
                'COMPLETIONTIME': '2026-11-06T10:00:00Z',
                'REGISTRATION': '2026-11-06T10:01:00Z',
            }
        ],
        [
            {
                'ID': '72',
                'TYPE': 'LOAD',
                'VOYAGE_ID': '900',
                'LOCATION_ID': '101',
                'COMPLETIONTIME': '2026-11-08T10:00:00Z',
                'REGISTRATION': '2026-11-08T10:01:00Z',
                'CARGO_ID': '13',
            }
        ],
    )
    _rewrite_table(
        snapshot,
        'LEG',
        lambda rows: [
            {
                **rows[0],
                'LOAD_TIME': '2026-11-08T11:00:00Z',
                'UNLOAD_TIME': '2026-11-08T20:00:00Z',
                'LOAD_LOCATION_ID': '101',
                'UNLOAD_LOCATION_ID': '102',
            }
        ],
        [
            {
                'ID': '82',
                'LOAD_TIME': '2026-11-09T10:00:00Z',
                'UNLOAD_TIME': '2026-11-10T20:00:00Z',
                'LOAD_LOCATION_ID': '102',
                'UNLOAD_LOCATION_ID': '103',
                'VOYAGE_ID': '900',
                'CARGO_ID': '13',
            }
        ],
    )
    _rewrite_table(
        snapshot,
        'CARRIER_MOVEMENT',
        lambda rows: [
            {
                **rows[0],
                'DEPARTURE_TIME': '2026-11-08T08:00:00Z',
                'ARRIVAL_TIME': '2026-11-08T20:00:00Z',
                'DEPARTURE_LOCATION_ID': '101',
                'ARRIVAL_LOCATION_ID': '102',
            }
        ],
        [
            {
                'ID': '92',
                'DEPARTURE_TIME': '2026-11-09T08:00:00Z',
                'ARRIVAL_TIME': '2026-11-09T20:00:00Z',
                'DEPARTURE_LOCATION_ID': '102',
                'ARRIVAL_LOCATION_ID': '103',
                'VOYAGE_ID': '900',
            }
        ],
    )
    call_command('load_data_snapshot', snapshot=str(snapshot), mapping=str(MAPPING))


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_matches_handling_history(loaded_snapshot):
    cargo_repository = DjangoCargoRepository()
    events = DjangoHandlingEventRepository()

    for cargo in cargo_repository.find_all():
        history = events.lookup_handling_history_of_cargo(cargo.tracking_id)
        expected = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            calculated_at=cargo.delivery.calculated_at,
        )

        assert replace(cargo.delivery, eta=None, last_event_id=None) == replace(expected, eta=None)
        assert cargo.delivery.eta.date() == expected.eta.date()
        assert cargo.delivery.last_event_id == history.most_recent_event_id


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(loaded_snapshot):
    for cargo in CargoRecord.objects.all():
        legs = list(LegRecord.objects.filter(cargo=cargo).order_by('load_time', 'pk'))
        assert all(
            previous.unload_location_id == following.load_location_id
            for previous, following in itertools.pairwise(legs)
        )


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_events_reference_existing_voyages_and_locations(loaded_snapshot):
    for event in HandlingEventRecord.objects.all():
        assert LocationRecord.objects.filter(pk=event.location_id).exists()
        assert event.voyage_id is None or VoyageRecord.objects.filter(pk=event.voyage_id).exists()


@pytest.mark.django_db(transaction=True)
def test_loaded_voyage_movements_form_ordered_schedules(loaded_snapshot):
    for voyage in VoyageRecord.objects.all():
        movements = list(
            CarrierMovementRecord.objects.filter(voyage=voyage).order_by('departure_time', 'pk')
        )
        assert all(movement.departure_time <= movement.arrival_time for movement in movements)
        assert all(
            previous.arrival_time <= following.departure_time
            for previous, following in itertools.pairwise(movements)
        )
