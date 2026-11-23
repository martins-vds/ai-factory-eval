import csv
import hashlib
import json
import shutil
from itertools import pairwise
from pathlib import Path

import pytest
from django.core.management import call_command

from cargotracker.cargo.domain.delivery import Delivery
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.models import HandlingEventRecord
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.voyage.infrastructure.models import CarrierMovementRecord

FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
ROOT = Path(__file__).resolve().parents[2]
MAPPING = ROOT / '.migration' / 'data' / 'mapping.yaml'


def _update_table(snapshot, table, updates, additional_rows=()):
    path = snapshot / f'{table}.csv'
    with path.open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        fieldnames = reader.fieldnames
        rows = list(reader)

    for row in rows:
        row.update(updates.get(row['ID'], {}))
    rows.extend(additional_rows)

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


def _row(**values):
    return values


def _load_invariant_snapshot(tmp_path):
    snapshot = tmp_path / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)
    _update_table(
        snapshot,
        'LOCATION',
        {},
        [_row(ID='103', UNLOCODE='GBFXT', NAME='Felixstowe')],
    )
    _update_table(
        snapshot,
        'CARGO',
        {
            '13': {
                'SPEC_DESTINATION_ID': '103',
                'TRANSPORT_STATUS': 'ONBOARD_CARRIER',
                'LAST_KNOWN_LOCATION_ID': '101',
                'CURRENT_VOYAGE_ID': '900',
                'MISDIRECTED': 'false',
                'ETA': '2026-11-10',
                'NEXT_EXPECTED_HANDLING_EVENT_TYPE': 'UNLOAD',
                'NEXT_EXPECTED_LOCATION_ID': '102',
                'NEXT_EXPECTED_VOYAGE_ID': '900',
                'ROUTING_STATUS': 'ROUTED',
                'LAST_EVENT_ID': '72',
            }
        },
    )
    _update_table(
        snapshot,
        'HANDLINGEVENT',
        {'71': {'VOYAGE_ID': r'\N', 'LOCATION_ID': '101'}},
        [
            _row(
                ID='72',
                TYPE='LOAD',
                VOYAGE_ID='900',
                LOCATION_ID='101',
                COMPLETIONTIME='2026-11-08T09:00:00Z',
                REGISTRATION='2026-11-08T09:01:00Z',
                CARGO_ID='13',
            )
        ],
    )
    _update_table(
        snapshot,
        'LEG',
        {
            '81': {
                'LOAD_TIME': '2026-11-09T10:00:00Z',
                'UNLOAD_TIME': '2026-11-09T12:00:00Z',
            }
        },
        [
            _row(
                ID='82',
                LOAD_TIME='2026-11-10T10:00:00Z',
                UNLOAD_TIME='2026-11-10T12:00:00Z',
                LOAD_LOCATION_ID='102',
                UNLOAD_LOCATION_ID='103',
                VOYAGE_ID='900',
                CARGO_ID='13',
            )
        ],
    )
    _update_table(
        snapshot,
        'CARRIER_MOVEMENT',
        {
            '91': {
                'ARRIVAL_TIME': '2026-11-09T12:00:00Z',
                'DEPARTURE_TIME': '2026-11-09T10:00:00Z',
            }
        },
        [
            _row(
                ID='92',
                ARRIVAL_TIME='2026-11-10T12:00:00Z',
                DEPARTURE_TIME='2026-11-10T10:00:00Z',
                ARRIVAL_LOCATION_ID='103',
                DEPARTURE_LOCATION_ID='102',
                VOYAGE_ID='900',
            )
        ],
    )
    call_command(
        'load_data_snapshot',
        snapshot=str(snapshot),
        mapping=str(MAPPING),
    )


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_matches_handling_history(tmp_path):
    _load_invariant_snapshot(tmp_path)
    cargo_repository = DjangoCargoRepository()
    history_repository = DjangoHandlingEventRepository()

    cargos = cargo_repository.find_all()
    assert cargos
    for cargo in cargos:
        history = history_repository.lookup_handling_history_of_cargo(cargo.tracking_id)
        derived = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            calculated_at=cargo.delivery.calculated_at,
        )

        assert cargo.delivery.transport_status == derived.transport_status
        assert cargo.delivery.last_known_location == derived.last_known_location
        assert cargo.delivery.current_voyage == derived.current_voyage
        assert cargo.delivery.misdirected == derived.misdirected
        stored_eta = cargo.delivery.eta.date() if cargo.delivery.eta is not None else None
        derived_eta = derived.eta.date() if derived.eta is not None else None
        assert stored_eta == derived_eta
        assert cargo.delivery.next_expected_activity == derived.next_expected_activity
        assert cargo.delivery.unloaded_at_destination == derived.unloaded_at_destination
        assert cargo.delivery.routing_status == derived.routing_status
        assert cargo.delivery.last_event_id == history.most_recent_event_id


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(tmp_path):
    _load_invariant_snapshot(tmp_path)

    cargos = DjangoCargoRepository().find_all()
    assert cargos
    assert all(len(cargo.itinerary.legs) > 1 for cargo in cargos)
    for cargo in cargos:
        for previous, current in pairwise(cargo.itinerary.legs):
            assert previous.unload_location == current.load_location
            assert previous.unload_time <= current.load_time


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_events_reference_existing_voyages_and_locations(tmp_path):
    _load_invariant_snapshot(tmp_path)

    events = HandlingEventRecord.objects.select_related('location', 'voyage')
    assert events.exists()
    for event in events:
        assert event.location_id is not None
        assert event.location.pk == event.location_id
        if event.event_type in ('LOAD', 'UNLOAD'):
            assert event.voyage_id is not None
        if event.voyage_id is not None:
            assert event.voyage.pk == event.voyage_id


@pytest.mark.django_db(transaction=True)
def test_loaded_voyage_carrier_movements_are_in_schedule_order(tmp_path):
    _load_invariant_snapshot(tmp_path)

    voyage_ids = CarrierMovementRecord.objects.values_list('voyage_id', flat=True).distinct()
    assert voyage_ids
    for voyage_id in voyage_ids:
        movements = list(
            CarrierMovementRecord.objects.filter(voyage_id=voyage_id).order_by(
                'departure_time', 'pk'
            )
        )
        assert len(movements) > 1
        for movement in movements:
            assert movement.departure_time < movement.arrival_time
        for previous, current in pairwise(movements):
            assert previous.arrival_time <= current.departure_time
            assert previous.arrival_location_id == current.departure_location_id
