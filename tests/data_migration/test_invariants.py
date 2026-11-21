import csv
import hashlib
import json
import shutil
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

SNAPSHOT_FIXTURE = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = Path(__file__).resolve().parents[2] / '.migration' / 'data' / 'mapping.yaml'


def _read_rows(snapshot, source):
    with (snapshot / f'{source}.csv').open(newline='', encoding='utf-8') as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def _write_rows(snapshot, source, rows):
    columns, _ = _read_rows(snapshot, source)
    with (snapshot / f'{source}.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def _write_invariant_snapshot(snapshot):
    shutil.copytree(SNAPSHOT_FIXTURE, snapshot)

    _, locations = _read_rows(snapshot, 'LOCATION')
    locations.append({'ID': '103', 'UNLOCODE': 'DEHAM', 'NAME': 'Hamburg'})
    _write_rows(snapshot, 'LOCATION', locations)

    _, voyages = _read_rows(snapshot, 'VOYAGE')
    voyages[0]['VOYAGE_NUMBER'] = 'V001'
    _write_rows(snapshot, 'VOYAGE', voyages)

    _, cargos = _read_rows(snapshot, 'CARGO')
    cargos[0].update(
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
        CALCULATED_AT='2026-11-08T08:02:00Z',
        LAST_EVENT_ID='71',
    )
    _write_rows(snapshot, 'CARGO', cargos)

    _, events = _read_rows(snapshot, 'HANDLINGEVENT')
    events[0].update(
        TYPE='LOAD',
        VOYAGE_ID='900',
        LOCATION_ID='101',
        COMPLETIONTIME='2026-11-08T08:00:00Z',
        REGISTRATION='2026-11-08T08:01:00Z',
    )
    events.append(
        {
            'ID': '70',
            'TYPE': 'RECEIVE',
            'VOYAGE_ID': r'\N',
            'LOCATION_ID': '101',
            'COMPLETIONTIME': '2026-11-07T10:00:00Z',
            'REGISTRATION': '2026-11-07T10:01:00Z',
            'CARGO_ID': '13',
        }
    )
    _write_rows(snapshot, 'HANDLINGEVENT', events)

    _write_rows(
        snapshot,
        'LEG',
        [
            {
                'ID': '81',
                'LOAD_TIME': '2026-11-08T08:00:00Z',
                'UNLOAD_TIME': '2026-11-09T10:00:00Z',
                'LOAD_LOCATION_ID': '101',
                'UNLOAD_LOCATION_ID': '102',
                'VOYAGE_ID': '900',
                'CARGO_ID': '13',
            },
            {
                'ID': '82',
                'LOAD_TIME': '2026-11-09T11:00:00Z',
                'UNLOAD_TIME': '2026-11-10T08:00:00Z',
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
                'ARRIVAL_TIME': '2026-11-09T10:00:00Z',
                'DEPARTURE_TIME': '2026-11-08T08:00:00Z',
                'ARRIVAL_LOCATION_ID': '102',
                'DEPARTURE_LOCATION_ID': '101',
                'VOYAGE_ID': '900',
            },
            {
                'ID': '92',
                'ARRIVAL_TIME': '2026-11-10T08:00:00Z',
                'DEPARTURE_TIME': '2026-11-09T11:00:00Z',
                'ARRIVAL_LOCATION_ID': '103',
                'DEPARTURE_LOCATION_ID': '102',
                'VOYAGE_ID': '900',
            },
        ],
    )

    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for source in ('LOCATION', 'VOYAGE', 'CARGO', 'HANDLINGEVENT', 'LEG', 'CARRIER_MOVEMENT'):
        path = snapshot / f'{source}.csv'
        _, rows = _read_rows(snapshot, source)
        manifest['tables'][source].update(
            rows=len(rows),
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        )
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')


@pytest.fixture
def loaded_snapshot(tmp_path):
    snapshot = tmp_path / 'snapshot'
    _write_invariant_snapshot(snapshot)
    call_command('load_data_snapshot', snapshot=str(snapshot), mapping=str(MAPPING))
    return snapshot


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_state_matches_its_handling_history(loaded_snapshot):
    cargo_repository = DjangoCargoRepository()
    event_repository = DjangoHandlingEventRepository()
    records = list(CargoRecord.objects.order_by('pk'))
    assert records

    for record in records:
        tracking_id = TrackingId(record.tracking_id)
        cargo = cargo_repository.find(tracking_id)
        history = event_repository.lookup_handling_history_of_cargo(tracking_id)
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
        assert (cargo.delivery.eta.date() if cargo.delivery.eta is not None else None) == (
            derived.eta.date() if derived.eta is not None else None
        )
        assert cargo.delivery.next_expected_activity == derived.next_expected_activity
        assert cargo.delivery.unloaded_at_destination == derived.unloaded_at_destination
        assert cargo.delivery.routing_status == derived.routing_status
        assert cargo.delivery.last_event_id == history.most_recent_event_id


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(loaded_snapshot):
    for cargo in CargoRecord.objects.all():
        legs = list(cargo.legs.order_by('load_time', 'pk'))
        assert len(legs) >= 2
        assert all(
            previous.unload_location_id == following.load_location_id
            for previous, following in pairwise(legs)
        )


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_event_references_exist(loaded_snapshot):
    location_ids = set(LocationRecord.objects.values_list('pk', flat=True))
    voyage_ids = set(VoyageRecord.objects.values_list('pk', flat=True))
    events = list(HandlingEventRecord.objects.all())
    assert events

    for event in events:
        assert event.location_id in location_ids
        if event.event_type in ('LOAD', 'UNLOAD'):
            assert event.voyage_id is not None
        if event.voyage_id is not None:
            assert event.voyage_id in voyage_ids


@pytest.mark.django_db(transaction=True)
def test_loaded_voyage_schedules_are_in_order(loaded_snapshot):
    voyages = list(VoyageRecord.objects.all())
    assert voyages
    for voyage in voyages:
        movements = list(
            CarrierMovementRecord.objects.filter(voyage=voyage).order_by('departure_time', 'pk')
        )
        assert len(movements) >= 2
        for movement in movements:
            assert movement.departure_time < movement.arrival_time
        for previous, following in pairwise(movements):
            assert previous.arrival_time <= following.departure_time
            assert previous.arrival_location_id == following.departure_location_id
