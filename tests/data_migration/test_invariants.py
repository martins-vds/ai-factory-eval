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

    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest['tables'][table].update(
        rows=len(rows),
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
    )
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')


def _load_coherent_fixture(tmp_path):
    snapshot = tmp_path / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)

    locations = _read_rows(snapshot, 'LOCATION')
    locations.append({'ID': '103', 'UNLOCODE': 'BEANR', 'NAME': 'Antwerp'})
    _write_rows(snapshot, 'LOCATION', locations)

    cargo = _read_rows(snapshot, 'CARGO')[0]
    cargo.update(
        SPEC_DESTINATION_ID='103',
        TRANSPORT_STATUS='ONBOARD_CARRIER',
        LAST_KNOWN_LOCATION_ID='101',
        CURRENT_VOYAGE_ID='900',
        MISDIRECTED='false',
        ETA='2026-11-11',
        NEXT_EXPECTED_HANDLING_EVENT_TYPE='UNLOAD',
        NEXT_EXPECTED_LOCATION_ID='102',
        NEXT_EXPECTED_VOYAGE_ID='900',
        UNLOADED_AT_DEST='false',
        ROUTING_STATUS='ROUTED',
        CALCULATED_AT='2026-11-07T11:02:00Z',
        LAST_EVENT_ID='71',
    )
    _write_rows(snapshot, 'CARGO', [cargo])

    _write_rows(
        snapshot,
        'HANDLINGEVENT',
        [
            {
                'ID': '70',
                'TYPE': 'RECEIVE',
                'VOYAGE_ID': r'\N',
                'LOCATION_ID': '101',
                'COMPLETIONTIME': '2026-11-07T10:12:13Z',
                'REGISTRATION': '2026-11-07T10:13:14Z',
                'CARGO_ID': '13',
            },
            {
                'ID': '71',
                'TYPE': 'LOAD',
                'VOYAGE_ID': '900',
                'LOCATION_ID': '101',
                'COMPLETIONTIME': '2026-11-07T11:00:00Z',
                'REGISTRATION': '2026-11-07T11:01:00Z',
                'CARGO_ID': '13',
            },
        ],
    )

    _write_rows(
        snapshot,
        'LEG',
        [
            {
                'ID': '81',
                'LOAD_TIME': '2026-11-08T08:00:00Z',
                'UNLOAD_TIME': '2026-11-09T11:00:00Z',
                'LOAD_LOCATION_ID': '101',
                'UNLOAD_LOCATION_ID': '102',
                'VOYAGE_ID': '900',
                'CARGO_ID': '13',
            },
            {
                'ID': '82',
                'LOAD_TIME': '2026-11-10T08:00:00Z',
                'UNLOAD_TIME': '2026-11-11T11:00:00Z',
                'LOAD_LOCATION_ID': '102',
                'UNLOAD_LOCATION_ID': '103',
                'VOYAGE_ID': '900',
                'CARGO_ID': '13',
            },
        ],
    )

    _write_rows(
        snapshot,
        'CARRIER_MOVEMENT',
        [
            {
                'ID': '91',
                'ARRIVAL_TIME': '2026-11-09T11:00:00Z',
                'DEPARTURE_TIME': '2026-11-08T08:00:00Z',
                'ARRIVAL_LOCATION_ID': '102',
                'DEPARTURE_LOCATION_ID': '101',
                'VOYAGE_ID': '900',
            },
            {
                'ID': '92',
                'ARRIVAL_TIME': '2026-11-11T11:00:00Z',
                'DEPARTURE_TIME': '2026-11-10T08:00:00Z',
                'ARRIVAL_LOCATION_ID': '103',
                'DEPARTURE_LOCATION_ID': '102',
                'VOYAGE_ID': '900',
            },
        ],
    )

    call_command(
        'load_data_snapshot',
        snapshot=str(snapshot),
        mapping=str(MAPPING),
    )


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_matches_its_route_and_handling_history(tmp_path):
    _load_coherent_fixture(tmp_path)

    cargo_repository = DjangoCargoRepository()
    history_repository = DjangoHandlingEventRepository()
    for cargo in cargo_repository.find_all():
        history = history_repository.lookup_handling_history_of_cargo(cargo.tracking_id)
        expected = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            calculated_at=cargo.delivery.calculated_at,
        )

        if expected.eta is None:
            assert cargo.delivery.eta is None
        else:
            assert cargo.delivery.eta.date() == expected.eta.date()
        assert cargo.delivery == replace(
            expected,
            eta=cargo.delivery.eta,
            last_event_id=history.most_recent_event_id,
        )


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(tmp_path):
    _load_coherent_fixture(tmp_path)

    for cargo in DjangoCargoRepository().find_all():
        legs = cargo.itinerary.legs
        assert len(legs) > 1
        assert all(
            first.unload_location == following.load_location
            for first, following in itertools.pairwise(legs)
        )


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_event_references_exist(tmp_path):
    _load_coherent_fixture(tmp_path)

    location_ids = set(LocationRecord.objects.values_list('pk', flat=True))
    voyage_ids = set(VoyageRecord.objects.values_list('pk', flat=True))
    events = list(HandlingEventRecord.objects.all())

    assert events
    for event in events:
        assert event.location_id in location_ids
        assert event.voyage_id is None or event.voyage_id in voyage_ids


@pytest.mark.django_db(transaction=True)
def test_loaded_carrier_movement_schedules_are_ordered(tmp_path):
    _load_coherent_fixture(tmp_path)

    for voyage in VoyageRecord.objects.all():
        movements = list(
            CarrierMovementRecord.objects.filter(voyage=voyage).order_by('departure_time', 'pk')
        )
        assert len(movements) > 1
        assert all(movement.departure_time < movement.arrival_time for movement in movements)
        assert all(
            current.arrival_time <= following.departure_time
            for current, following in itertools.pairwise(movements)
        )
