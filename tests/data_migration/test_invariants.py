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

FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = Path(__file__).resolve().parents[2] / '.migration' / 'data' / 'mapping.yaml'


def _read_table(snapshot, table):
    with (snapshot / f'{table}.csv').open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def _write_table(snapshot, table, header, rows):
    with (snapshot / f'{table}.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


def _make_invariant_snapshot(snapshot):
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)

    header, rows = _read_table(snapshot, 'LOCATION')
    rows.append({'ID': '103', 'UNLOCODE': 'BEANR', 'NAME': 'Antwerp'})
    _write_table(snapshot, 'LOCATION', header, rows)

    header, rows = _read_table(snapshot, 'CARGO')
    rows[0].update(
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
    )
    _write_table(snapshot, 'CARGO', header, rows)

    header, rows = _read_table(snapshot, 'HANDLINGEVENT')
    rows[0].update(TYPE='LOAD', LOCATION_ID='101')
    _write_table(snapshot, 'HANDLINGEVENT', header, rows)

    header, rows = _read_table(snapshot, 'LEG')
    rows[0].update(
        LOAD_TIME='2026-11-08T08:00:00Z',
        UNLOAD_TIME='2026-11-09T10:00:00Z',
    )
    rows.append(
        {
            'ID': '82',
            'LOAD_TIME': '2026-11-09T10:00:00Z',
            'UNLOAD_TIME': '2026-11-10T10:00:00Z',
            'LOAD_LOCATION_ID': '102',
            'UNLOAD_LOCATION_ID': '103',
            'VOYAGE_ID': '900',
            'CARGO_ID': '13',
        }
    )
    _write_table(snapshot, 'LEG', header, rows)

    header, rows = _read_table(snapshot, 'CARRIER_MOVEMENT')
    rows[0].update(
        ARRIVAL_TIME='2026-11-09T10:00:00Z',
        DEPARTURE_TIME='2026-11-08T08:00:00Z',
    )
    rows.append(
        {
            'ID': '92',
            'ARRIVAL_TIME': '2026-11-10T10:00:00Z',
            'DEPARTURE_TIME': '2026-11-09T10:00:00Z',
            'ARRIVAL_LOCATION_ID': '103',
            'DEPARTURE_LOCATION_ID': '102',
            'VOYAGE_ID': '900',
        }
    )
    _write_table(snapshot, 'CARRIER_MOVEMENT', header, rows)

    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for table, details in manifest['tables'].items():
        path = snapshot / f'{table}.csv'
        with path.open(encoding='utf-8', newline='') as stream:
            details['rows'] = sum(1 for _ in csv.reader(stream)) - 1
        details['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')


@pytest.fixture
def loaded_invariant_snapshot(tmp_path):
    snapshot = tmp_path / 'snapshot'
    _make_invariant_snapshot(snapshot)
    call_command(
        'load_data_snapshot',
        snapshot=str(snapshot),
        mapping=str(MAPPING),
    )


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_state_matches_its_handling_history(loaded_invariant_snapshot):
    cargo_repository = DjangoCargoRepository()
    handling_repository = DjangoHandlingEventRepository()
    cargos = list(CargoRecord.objects.order_by('pk'))

    assert cargos
    for record in cargos:
        cargo = cargo_repository.find(TrackingId(record.tracking_id))
        history = handling_repository.lookup_handling_history_of_cargo(cargo.tracking_id)
        derived = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            calculated_at=cargo.delivery.calculated_at,
        )
        stored = cargo.delivery

        assert derived.transport_status == stored.transport_status
        assert derived.last_known_location == stored.last_known_location
        assert derived.current_voyage == stored.current_voyage
        assert derived.misdirected == stored.misdirected
        assert (derived.eta.date() if derived.eta else None) == (
            stored.eta.date() if stored.eta else None
        )
        assert derived.next_expected_activity == stored.next_expected_activity
        assert derived.unloaded_at_destination == stored.unloaded_at_destination
        assert derived.routing_status == stored.routing_status
        assert history.most_recent_event_id == stored.last_event_id


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(loaded_invariant_snapshot):
    itineraries = [
        cargo.itinerary for cargo in DjangoCargoRepository().find_all() if cargo.itinerary.legs
    ]

    assert any(len(itinerary.legs) > 1 for itinerary in itineraries)
    for itinerary in itineraries:
        assert all(
            current.unload_location == following.load_location
            for current, following in pairwise(itinerary.legs)
        )


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_events_reference_existing_voyages_and_locations(
    loaded_invariant_snapshot,
):
    events = list(HandlingEventRecord.objects.all())

    assert events
    for event in events:
        assert event.voyage_id is not None
        assert VoyageRecord.objects.filter(pk=event.voyage_id).exists()
        assert event.location_id is not None
        assert LocationRecord.objects.filter(pk=event.location_id).exists()


@pytest.mark.django_db(transaction=True)
def test_loaded_carrier_movement_schedules_are_in_order(loaded_invariant_snapshot):
    voyages_with_multiple_movements = 0
    for voyage in VoyageRecord.objects.order_by('pk'):
        movements = list(
            CarrierMovementRecord.objects.filter(voyage=voyage).order_by('departure_time', 'pk')
        )
        if len(movements) > 1:
            voyages_with_multiple_movements += 1
        assert all(movement.departure_time <= movement.arrival_time for movement in movements)
        assert all(
            current.arrival_time <= following.departure_time
            for current, following in pairwise(movements)
        )

    assert voyages_with_multiple_movements
