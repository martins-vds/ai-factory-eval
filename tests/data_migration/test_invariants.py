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
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.models import HandlingEventRecord
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.models import LocationRecord
from cargotracker.voyage.infrastructure.models import CarrierMovementRecord, VoyageRecord

FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = Path(__file__).resolve().parents[2] / '.migration' / 'data' / 'mapping.yaml'


def _rewrite_rows(snapshot, table, updates=None, additions=()):
    path = snapshot / f'{table}.csv'
    with path.open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        fieldnames = reader.fieldnames
        rows = list(reader)
    for row in rows:
        row.update(updates or {})
    rows.extend(additions)
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


def _prepare_snapshot(snapshot):
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)
    _rewrite_rows(
        snapshot,
        'LOCATION',
        additions=[{'ID': '103', 'UNLOCODE': 'SGSIN', 'NAME': 'Singapore'}],
    )
    _rewrite_rows(
        snapshot,
        'CARGO',
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
        },
    )
    _rewrite_rows(
        snapshot,
        'HANDLINGEVENT',
        {
            'TYPE': 'LOAD',
            'LOCATION_ID': '101',
            'COMPLETIONTIME': '2026-11-07T10:12:13+02:00',
        },
    )
    _rewrite_rows(
        snapshot,
        'CARRIER_MOVEMENT',
        {
            'DEPARTURE_TIME': '2026-11-08T09:00:00Z',
            'ARRIVAL_TIME': '2026-11-09T10:00:00Z',
        },
        additions=[
            {
                'ID': '92',
                'ARRIVAL_TIME': '2026-11-10T00:00:00Z',
                'DEPARTURE_TIME': '2026-11-09T12:00:00Z',
                'ARRIVAL_LOCATION_ID': '103',
                'DEPARTURE_LOCATION_ID': '102',
                'VOYAGE_ID': '900',
            }
        ],
    )
    _rewrite_rows(
        snapshot,
        'LEG',
        additions=[
            {
                'ID': '82',
                'LOAD_TIME': '2026-11-09T12:00:00Z',
                'UNLOAD_TIME': '2026-11-10T00:00:00Z',
                'LOAD_LOCATION_ID': '102',
                'UNLOAD_LOCATION_ID': '103',
                'VOYAGE_ID': '900',
                'CARGO_ID': '13',
            }
        ],
    )


def _load_snapshot(tmp_path):
    snapshot = tmp_path / 'snapshot'
    _prepare_snapshot(snapshot)
    call_command('load_data_snapshot', snapshot=str(snapshot), mapping=str(MAPPING))


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_matches_its_handling_history(tmp_path):
    _load_snapshot(tmp_path)
    cargo_repository = DjangoCargoRepository()
    history_repository = DjangoHandlingEventRepository()

    for cargo in cargo_repository.find_all():
        history = history_repository.lookup_handling_history_of_cargo(cargo.tracking_id)
        derived = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            calculated_at=cargo.delivery.calculated_at,
        )

        assert replace(derived, last_event_id=history.most_recent_event_id) == cargo.delivery


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(tmp_path):
    _load_snapshot(tmp_path)

    for cargo in DjangoCargoRepository().find_all():
        legs = cargo.itinerary.legs
        assert len(legs) >= 2
        for first, following in itertools.pairwise(legs):
            assert first.unload_location == following.load_location


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_events_reference_existing_voyages_and_locations(tmp_path):
    _load_snapshot(tmp_path)
    voyage_ids = set(VoyageRecord.objects.values_list('pk', flat=True))
    location_ids = set(LocationRecord.objects.values_list('pk', flat=True))

    for event in HandlingEventRecord.objects.all():
        assert event.location_id in location_ids
        assert event.voyage_id is None or event.voyage_id in voyage_ids


@pytest.mark.django_db(transaction=True)
def test_loaded_carrier_movements_form_an_ordered_voyage_schedule(tmp_path):
    _load_snapshot(tmp_path)

    for voyage in VoyageRecord.objects.all():
        movements = list(
            CarrierMovementRecord.objects.filter(voyage=voyage).order_by('departure_time', 'pk')
        )
        assert len(movements) >= 2
        for movement in movements:
            assert movement.departure_time <= movement.arrival_time
        for first, following in itertools.pairwise(movements):
            assert first.arrival_time <= following.departure_time
            assert first.arrival_location_id == following.departure_location_id
