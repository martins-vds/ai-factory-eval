import csv
import hashlib
import json
import shutil
from dataclasses import replace
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
MAPPING = Path(__file__).parents[2] / '.migration' / 'data' / 'mapping.yaml'


def _read_table(snapshot, source):
    with (snapshot / f'{source}.csv').open(newline='', encoding='utf-8') as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def _write_table(snapshot, source, headers, rows):
    with (snapshot / f'{source}.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def _load_invariant_fixture(tmp_path):
    snapshot = tmp_path / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)

    location_headers, locations = _read_table(snapshot, 'LOCATION')
    locations.append({'ID': '103', 'UNLOCODE': 'FISEL', 'NAME': 'Helsinki'})
    _write_table(snapshot, 'LOCATION', location_headers, locations)

    cargo_headers, cargos = _read_table(snapshot, 'CARGO')
    cargo = cargos[0]
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
    )
    _write_table(snapshot, 'CARGO', cargo_headers, cargos)

    event_headers, events = _read_table(snapshot, 'HANDLINGEVENT')
    events[0].update(TYPE='LOAD', LOCATION_ID='101')
    _write_table(snapshot, 'HANDLINGEVENT', event_headers, events)

    leg_headers, legs = _read_table(snapshot, 'LEG')
    legs[0].update(
        LOAD_TIME='2026-11-08T00:00:00Z',
        UNLOAD_TIME='2026-11-09T00:00:00Z',
        UNLOAD_LOCATION_ID='102',
    )
    legs.append(
        {
            'ID': '82',
            'LOAD_TIME': '2026-11-10T00:00:00Z',
            'UNLOAD_TIME': '2026-11-11T00:00:00Z',
            'LOAD_LOCATION_ID': '102',
            'UNLOAD_LOCATION_ID': '103',
            'VOYAGE_ID': '900',
            'CARGO_ID': '13',
        }
    )
    _write_table(snapshot, 'LEG', leg_headers, legs)

    movement_headers, movements = _read_table(snapshot, 'CARRIER_MOVEMENT')
    movements[0].update(
        DEPARTURE_TIME='2026-11-08T00:00:00Z',
        ARRIVAL_TIME='2026-11-09T00:00:00Z',
    )
    movements.append(
        {
            'ID': '92',
            'ARRIVAL_TIME': '2026-11-11T00:00:00Z',
            'DEPARTURE_TIME': '2026-11-10T00:00:00Z',
            'ARRIVAL_LOCATION_ID': '103',
            'DEPARTURE_LOCATION_ID': '102',
            'VOYAGE_ID': '900',
        }
    )
    _write_table(snapshot, 'CARRIER_MOVEMENT', movement_headers, movements)

    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for source in ('LOCATION', 'CARGO', 'HANDLINGEVENT', 'LEG', 'CARRIER_MOVEMENT'):
        source_path = snapshot / f'{source}.csv'
        _, rows = _read_table(snapshot, source)
        manifest['tables'][source].update(
            rows=len(rows),
            sha256=hashlib.sha256(source_path.read_bytes()).hexdigest(),
        )
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')

    call_command('load_data_snapshot', snapshot=str(snapshot), mapping=str(MAPPING))


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_matches_its_handling_history(tmp_path):
    _load_invariant_fixture(tmp_path)
    cargo_repository = DjangoCargoRepository()
    history_repository = DjangoHandlingEventRepository()

    for cargo in cargo_repository.find_all():
        history = history_repository.lookup_handling_history_of_cargo(cargo.tracking_id)
        derived_delivery = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            calculated_at=cargo.delivery.calculated_at,
        )

        assert (
            replace(derived_delivery, last_event_id=history.most_recent_event_id)
            == cargo.delivery
        )


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(tmp_path):
    _load_invariant_fixture(tmp_path)
    connected_pairs = 0

    for cargo in CargoRecord.objects.prefetch_related('legs'):
        legs = list(cargo.legs.all())
        for current, following in zip(legs, legs[1:]):
            assert current.unload_location_id == following.load_location_id
            connected_pairs += 1

    assert connected_pairs > 0


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_events_reference_existing_voyages_and_locations(tmp_path):
    _load_invariant_fixture(tmp_path)
    events = list(HandlingEventRecord.objects.all())
    voyage_ids = set(VoyageRecord.objects.values_list('pk', flat=True))
    location_ids = set(LocationRecord.objects.values_list('pk', flat=True))

    assert events
    assert all(event.voyage_id in voyage_ids for event in events)
    assert all(event.location_id in location_ids for event in events)


@pytest.mark.django_db(transaction=True)
def test_loaded_carrier_movement_schedules_are_in_order(tmp_path):
    _load_invariant_fixture(tmp_path)
    checked_movements = 0

    for voyage in VoyageRecord.objects.all():
        movements = list(
            CarrierMovementRecord.objects.filter(voyage=voyage).order_by('departure_time', 'pk')
        )
        for movement in movements:
            assert movement.departure_time <= movement.arrival_time
            checked_movements += 1
        for previous, following in zip(movements, movements[1:]):
            assert previous.arrival_time <= following.departure_time
            assert previous.arrival_location_id == following.departure_location_id

    assert checked_movements > 0
