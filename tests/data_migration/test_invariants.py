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
from cargotracker.cargo.infrastructure.models import CargoRecord
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.models import HandlingEventRecord
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.models import LocationRecord
from cargotracker.voyage.infrastructure.models import CarrierMovementRecord, VoyageRecord

FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def _read_rows(snapshot, table):
    with (snapshot / f'{table}.csv').open(encoding='utf-8', newline='') as stream:
        return list(csv.DictReader(stream))


def _write_rows(snapshot, table, rows):
    path = snapshot / f'{table}.csv'
    with path.open(encoding='utf-8', newline='') as stream:
        fieldnames = next(csv.reader(stream))
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _prepare_snapshot(tmp_path):
    snapshot = tmp_path / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)

    cargo = _read_rows(snapshot, 'CARGO')[0]
    cargo.update(
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
    _write_rows(snapshot, 'CARGO', [cargo])

    events = _read_rows(snapshot, 'HANDLINGEVENT')
    events[0].update(TYPE='RECEIVE', VOYAGE_ID='\\N', LOCATION_ID='101')
    events.append(
        {
            'ID': '72',
            'TYPE': 'LOAD',
            'VOYAGE_ID': '900',
            'LOCATION_ID': '101',
            'COMPLETIONTIME': '2026-11-08T08:00:00Z',
            'REGISTRATION': '2026-11-08T08:01:00Z',
            'CARGO_ID': '13',
        }
    )
    _write_rows(snapshot, 'HANDLINGEVENT', events)

    legs = _read_rows(snapshot, 'LEG')
    legs.append(
        {
            'ID': '82',
            'LOAD_TIME': '2026-11-09T12:00:00Z',
            'UNLOAD_TIME': '2026-11-10T12:00:00Z',
            'LOAD_LOCATION_ID': '102',
            'UNLOAD_LOCATION_ID': '102',
            'VOYAGE_ID': '900',
            'CARGO_ID': '13',
        }
    )
    _write_rows(snapshot, 'LEG', legs)

    movements = _read_rows(snapshot, 'CARRIER_MOVEMENT')
    movements.append(
        {
            'ID': '92',
            'ARRIVAL_TIME': '2026-11-10T12:00:00Z',
            'DEPARTURE_TIME': '2026-11-09T12:00:00Z',
            'ARRIVAL_LOCATION_ID': '102',
            'DEPARTURE_LOCATION_ID': '102',
            'VOYAGE_ID': '900',
        }
    )
    _write_rows(snapshot, 'CARRIER_MOVEMENT', movements)

    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for table in ('CARGO', 'HANDLINGEVENT', 'LEG', 'CARRIER_MOVEMENT'):
        path = snapshot / f'{table}.csv'
        manifest['tables'][table].update(
            rows=len(_read_rows(snapshot, table)),
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        )
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
    return snapshot


def _load_snapshot(snapshot):
    call_command(
        'load_data_snapshot',
        snapshot=str(snapshot),
        mapping=str(REPOSITORY_ROOT / '.migration' / 'data' / 'mapping.yaml'),
    )


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_matches_its_handling_history(tmp_path):
    _load_snapshot(_prepare_snapshot(tmp_path))
    cargo_repository = DjangoCargoRepository()
    handling_event_repository = DjangoHandlingEventRepository()

    cargos = cargo_repository.find_all()
    assert cargos
    for cargo in cargos:
        history = handling_event_repository.lookup_handling_history_of_cargo(cargo.tracking_id)
        assert history.most_recent_event is not None
        assert cargo.delivery.last_event_id == history.most_recent_event_id
        derived_delivery = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            calculated_at=cargo.delivery.calculated_at,
        )

        if derived_delivery.eta is None:
            assert cargo.delivery.eta is None
        else:
            assert cargo.delivery.eta is not None
            assert derived_delivery.eta.date() == cargo.delivery.eta.date()
        assert (
            replace(
                derived_delivery,
                eta=cargo.delivery.eta,
                last_event_id=history.most_recent_event_id,
            )
            == cargo.delivery
        )


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(tmp_path):
    _load_snapshot(_prepare_snapshot(tmp_path))

    itineraries = [
        list(cargo.legs.order_by('load_time', 'pk'))
        for cargo in CargoRecord.objects.prefetch_related('legs')
    ]
    assert any(len(legs) > 1 for legs in itineraries)
    for legs in itineraries:
        for previous, following in pairwise(legs):
            assert previous.unload_location_id == following.load_location_id


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_events_reference_existing_voyages_and_locations(tmp_path):
    _load_snapshot(_prepare_snapshot(tmp_path))

    events = list(HandlingEventRecord.objects.all())
    location_ids = set(LocationRecord.objects.values_list('pk', flat=True))
    voyage_ids = set(VoyageRecord.objects.values_list('pk', flat=True))

    assert events
    assert any(event.voyage_id is not None for event in events)
    for event in events:
        assert event.location_id in location_ids
        assert event.voyage_id is None or event.voyage_id in voyage_ids


@pytest.mark.django_db(transaction=True)
def test_loaded_carrier_movement_schedules_are_ordered_and_connected(tmp_path):
    _load_snapshot(_prepare_snapshot(tmp_path))

    voyages = VoyageRecord.objects.all()
    assert voyages.exists()
    assert CarrierMovementRecord.objects.count() > 1
    for voyage in voyages:
        movements = list(
            CarrierMovementRecord.objects.filter(voyage=voyage).order_by('departure_time', 'pk')
        )
        for movement in movements:
            assert movement.departure_time <= movement.arrival_time
        for previous, following in pairwise(movements):
            assert previous.arrival_time <= following.departure_time
