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
from cargotracker.cargo.infrastructure.models import CargoRecord, LegRecord
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.models import HandlingEventRecord
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.models import LocationRecord
from cargotracker.voyage.infrastructure.models import CarrierMovementRecord, VoyageRecord

FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = Path(__file__).resolve().parents[2] / '.migration' / 'data' / 'mapping.yaml'


def _update_table(snapshot, table, updates=None, additions=()):
    path = snapshot / f'{table}.csv'
    with path.open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        fieldnames = reader.fieldnames
        rows = list(reader)

    for row in rows:
        row.update((updates or {}).get(row['ID'], {}))
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


def _load_snapshot(tmp_path):
    snapshot = tmp_path / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)
    _update_table(
        snapshot,
        'CARGO',
        {
            '13': {
                'TRANSPORT_STATUS': 'IN_PORT',
                'LAST_KNOWN_LOCATION_ID': '101',
                'CURRENT_VOYAGE_ID': '\\N',
                'MISDIRECTED': 'false',
                'ETA': '2026-11-11',
                'NEXT_EXPECTED_LOCATION_ID': '101',
                'NEXT_EXPECTED_VOYAGE_ID': '900',
            }
        },
    )
    _update_table(
        snapshot,
        'HANDLINGEVENT',
        {'71': {'LOCATION_ID': '101', 'VOYAGE_ID': '\\N'}},
    )
    _update_table(
        snapshot,
        'LEG',
        additions=[
            {
                'ID': '82',
                'LOAD_TIME': '2026-11-10T12:00:00Z',
                'UNLOAD_TIME': '2026-11-11T12:00:00Z',
                'LOAD_LOCATION_ID': '102',
                'UNLOAD_LOCATION_ID': '102',
                'VOYAGE_ID': '900',
                'CARGO_ID': '13',
            }
        ],
    )
    _update_table(
        snapshot,
        'CARRIER_MOVEMENT',
        additions=[
            {
                'ID': '92',
                'ARRIVAL_TIME': '2026-11-11T10:00:00Z',
                'DEPARTURE_TIME': '2026-11-10T12:00:00Z',
                'ARRIVAL_LOCATION_ID': '102',
                'DEPARTURE_LOCATION_ID': '102',
                'VOYAGE_ID': '900',
            }
        ],
    )
    call_command('load_data_snapshot', snapshot=str(snapshot), mapping=str(MAPPING))


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_state_matches_its_handling_history(tmp_path):
    _load_snapshot(tmp_path)
    cargo_repository = DjangoCargoRepository()
    event_repository = DjangoHandlingEventRepository()

    cargos = cargo_repository.find_all()
    assert cargos
    for cargo in cargos:
        history = event_repository.lookup_handling_history_of_cargo(cargo.tracking_id)
        derived_delivery = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            calculated_at=cargo.delivery.calculated_at,
        )

        assert derived_delivery.eta.date() == cargo.delivery.eta.date()
        assert replace(
            derived_delivery,
            eta=cargo.delivery.eta,
            last_event_id=history.most_recent_event_id,
        ) == cargo.delivery


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(tmp_path):
    _load_snapshot(tmp_path)

    cargos = CargoRecord.objects.all()
    assert cargos.exists()
    for cargo in cargos:
        legs = list(cargo.legs.order_by('load_time'))
        assert all(
            previous.unload_location_id == following.load_location_id
            for previous, following in pairwise(legs)
        )


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_events_reference_existing_voyages_and_locations(tmp_path):
    _load_snapshot(tmp_path)

    events = list(HandlingEventRecord.objects.all())
    voyage_ids = set(VoyageRecord.objects.values_list('id', flat=True))
    location_ids = set(LocationRecord.objects.values_list('id', flat=True))

    assert events
    assert all(
        event.voyage_id is None or event.voyage_id in voyage_ids for event in events
    )
    assert all(event.location_id in location_ids for event in events)


@pytest.mark.django_db(transaction=True)
def test_loaded_carrier_movements_form_ordered_voyage_schedules(tmp_path):
    _load_snapshot(tmp_path)

    schedules = {}
    movements = CarrierMovementRecord.objects.order_by('voyage_id', 'departure_time')
    assert movements.exists()
    for movement in movements:
        schedules.setdefault(movement.voyage_id, []).append(movement)

    for schedule in schedules.values():
        assert all(movement.departure_time <= movement.arrival_time for movement in schedule)
        assert all(
            previous.arrival_time <= following.departure_time
            for previous, following in pairwise(schedule)
        )
