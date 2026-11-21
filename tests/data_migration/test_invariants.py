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
MAPPING = Path(__file__).parents[2] / '.migration' / 'data' / 'mapping.yaml'


def _update_table(snapshot, table, update_rows):
    path = snapshot / f'{table}.csv'
    with path.open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        fieldnames = reader.fieldnames
        rows = list(reader)
    rows = update_rows(rows)
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest['tables'][table].update(
        rows=len(rows),
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
    )
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')


def _load_snapshot(tmp_path):
    snapshot = tmp_path / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)

    _update_table(
        snapshot,
        'CARGO',
        lambda rows: [
            {
                **rows[0],
                'TRANSPORT_STATUS': 'ONBOARD_CARRIER',
                'LAST_KNOWN_LOCATION_ID': '101',
                'CURRENT_VOYAGE_ID': '900',
                'MISDIRECTED': 'false',
                'ETA': '2026-11-11',
                'NEXT_EXPECTED_HANDLING_EVENT_TYPE': 'UNLOAD',
                'NEXT_EXPECTED_LOCATION_ID': '102',
                'NEXT_EXPECTED_VOYAGE_ID': '900',
            }
        ],
    )
    _update_table(
        snapshot,
        'HANDLINGEVENT',
        lambda rows: [{**rows[0], 'TYPE': 'LOAD', 'LOCATION_ID': '101'}],
    )
    _update_table(
        snapshot,
        'LEG',
        lambda rows: [
            *rows,
            {
                'ID': '82',
                'LOAD_TIME': '2026-11-10T12:00:00Z',
                'UNLOAD_TIME': '2026-11-11T12:00:00Z',
                'LOAD_LOCATION_ID': '102',
                'UNLOAD_LOCATION_ID': '102',
                'VOYAGE_ID': '900',
                'CARGO_ID': '13',
            },
        ],
    )
    _update_table(
        snapshot,
        'CARRIER_MOVEMENT',
        lambda rows: [
            *rows,
            {
                'ID': '92',
                'ARRIVAL_TIME': '2026-11-09T14:00:00Z',
                'DEPARTURE_TIME': '2026-11-09T12:00:00Z',
                'ARRIVAL_LOCATION_ID': '101',
                'DEPARTURE_LOCATION_ID': '102',
                'VOYAGE_ID': '900',
            },
        ],
    )
    call_command('load_data_snapshot', snapshot=str(snapshot), mapping=str(MAPPING))


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_matches_handling_history(tmp_path):
    _load_snapshot(tmp_path)

    for record in CargoRecord.objects.order_by('pk'):
        cargo = DjangoCargoRepository().find(TrackingId(record.tracking_id))
        history = DjangoHandlingEventRepository().lookup_handling_history_of_cargo(
            TrackingId(record.tracking_id)
        )
        derived = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            cargo.delivery.calculated_at,
        )

        assert (
            cargo.delivery.eta.date() if cargo.delivery.eta is not None else None
        ) == (derived.eta.date() if derived.eta is not None else None)
        assert replace(cargo.delivery, eta=derived.eta) == replace(
            derived,
            last_event_id=history.most_recent_event_id,
        )


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(tmp_path):
    _load_snapshot(tmp_path)

    for cargo in CargoRecord.objects.all():
        legs = list(cargo.legs.order_by('load_time', 'pk'))
        assert all(
            previous.unload_location_id == following.load_location_id
            for previous, following in pairwise(legs)
        )


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_events_reference_existing_voyages_and_locations(tmp_path):
    _load_snapshot(tmp_path)

    location_ids = set(LocationRecord.objects.values_list('pk', flat=True))
    voyage_ids = set(VoyageRecord.objects.values_list('pk', flat=True))

    for event in HandlingEventRecord.objects.all():
        assert event.location_id in location_ids
        assert event.voyage_id is None or event.voyage_id in voyage_ids


@pytest.mark.django_db(transaction=True)
def test_loaded_carrier_movements_form_an_ordered_schedule(tmp_path):
    _load_snapshot(tmp_path)

    for voyage in VoyageRecord.objects.all():
        movements = list(
            CarrierMovementRecord.objects.filter(voyage=voyage).order_by('departure_time', 'pk')
        )
        assert all(movement.departure_time <= movement.arrival_time for movement in movements)
        assert all(
            previous.arrival_time <= following.departure_time
            and previous.arrival_location_id == following.departure_location_id
            for previous, following in pairwise(movements)
        )
