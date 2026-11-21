import csv
import hashlib
import itertools
import json
import shutil
from pathlib import Path

import pytest
from django.core.management import call_command

from cargotracker.cargo.domain.delivery import Delivery
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.models import CargoRecord, LegRecord
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.models import HandlingEventRecord
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.models import LocationRecord
from cargotracker.voyage.infrastructure.models import CarrierMovementRecord, VoyageRecord

FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = Path(__file__).resolve().parents[2] / '.migration' / 'data' / 'mapping.yaml'


def _write_table(snapshot, table, rows):
    path = snapshot / f'{table}.csv'
    with path.open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        fieldnames = reader.fieldnames
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _load_invariant_snapshot(tmp_path):
    snapshot = tmp_path / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)

    locations = list(csv.DictReader((snapshot / 'LOCATION.csv').open(encoding='utf-8')))
    locations.append({'ID': '103', 'UNLOCODE': 'USLAX', 'NAME': 'Los Angeles'})
    _write_table(snapshot, 'LOCATION', locations)

    cargos = list(csv.DictReader((snapshot / 'CARGO.csv').open(encoding='utf-8')))
    cargos[0].update(
        TRANSPORT_STATUS='ONBOARD_CARRIER',
        LAST_KNOWN_LOCATION_ID='101',
        CURRENT_VOYAGE_ID='900',
        MISDIRECTED='false',
        ETA='2026-11-10',
        NEXT_EXPECTED_HANDLING_EVENT_TYPE='UNLOAD',
        NEXT_EXPECTED_LOCATION_ID='103',
        NEXT_EXPECTED_VOYAGE_ID='900',
    )
    _write_table(snapshot, 'CARGO', cargos)

    events = list(csv.DictReader((snapshot / 'HANDLINGEVENT.csv').open(encoding='utf-8')))
    events[0].update(
        TYPE='LOAD',
        LOCATION_ID='101',
        COMPLETIONTIME='2026-11-07T08:12:13Z',
        REGISTRATION='2026-11-07T10:13:14Z',
    )
    _write_table(snapshot, 'HANDLINGEVENT', events)

    legs = list(csv.DictReader((snapshot / 'LEG.csv').open(encoding='utf-8')))
    legs[0].update(
        LOAD_TIME='2026-11-08T11:00:00+03:00',
        UNLOAD_TIME='2026-11-09T14:00:00Z',
        LOAD_LOCATION_ID='101',
        UNLOAD_LOCATION_ID='103',
    )
    second_leg = dict(legs[0])
    second_leg.update(
        ID='82',
        LOAD_TIME='2026-11-09T15:00:00Z',
        UNLOAD_TIME='2026-11-10T11:00:00Z',
        LOAD_LOCATION_ID='103',
        UNLOAD_LOCATION_ID='102',
    )
    legs.append(second_leg)
    _write_table(snapshot, 'LEG', legs)

    movements = list(csv.DictReader((snapshot / 'CARRIER_MOVEMENT.csv').open(encoding='utf-8')))
    movements[0].update(
        ARRIVAL_TIME='2026-11-09T13:00:00Z',
        DEPARTURE_TIME='2026-11-08T12:00:00Z',
        ARRIVAL_LOCATION_ID='103',
        DEPARTURE_LOCATION_ID='101',
    )
    second_movement = dict(movements[0])
    second_movement.update(
        ID='92',
        ARRIVAL_TIME='2026-11-10T10:00:00Z',
        DEPARTURE_TIME='2026-11-09T14:00:00Z',
        ARRIVAL_LOCATION_ID='102',
        DEPARTURE_LOCATION_ID='103',
    )
    movements.append(second_movement)
    _write_table(snapshot, 'CARRIER_MOVEMENT', movements)

    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for table in ('LOCATION', 'CARGO', 'HANDLINGEVENT', 'LEG', 'CARRIER_MOVEMENT'):
        path = snapshot / f'{table}.csv'
        manifest['tables'][table].update(
            rows=sum(1 for _ in csv.DictReader(path.open(encoding='utf-8'))),
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        )
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
    call_command('load_data_snapshot', snapshot=str(snapshot), mapping=str(MAPPING))


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_state_matches_its_handling_history(tmp_path):
    _load_invariant_snapshot(tmp_path)

    repository = DjangoCargoRepository()
    events = DjangoHandlingEventRepository()
    for record in CargoRecord.objects.all():
        cargo = repository.find(TrackingId(record.tracking_id))
        history = events.lookup_handling_history_of_cargo(cargo.tracking_id)
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
        assert cargo.delivery.eta.date() == derived.eta.date()
        assert cargo.delivery.next_expected_activity == derived.next_expected_activity
        assert cargo.delivery.unloaded_at_destination == derived.unloaded_at_destination
        assert cargo.delivery.routing_status == derived.routing_status
        assert cargo.delivery.calculated_at == derived.calculated_at
        assert cargo.delivery.last_event_id == history.most_recent_event_id


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(tmp_path):
    _load_invariant_snapshot(tmp_path)

    for cargo in CargoRecord.objects.all():
        legs = list(
            LegRecord.objects.filter(cargo=cargo)
            .select_related('load_location', 'unload_location')
            .order_by('load_time', 'pk')
        )

        assert len(legs) >= 2
        assert all(
            previous.unload_location_id == following.load_location_id
            for previous, following in itertools.pairwise(legs)
        )


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_event_references_exist(tmp_path):
    _load_invariant_snapshot(tmp_path)

    location_ids = set(LocationRecord.objects.values_list('pk', flat=True))
    voyage_ids = set(VoyageRecord.objects.values_list('pk', flat=True))
    for event in HandlingEventRecord.objects.all():
        assert event.location_id in location_ids
        if event.voyage_id is not None:
            assert event.voyage_id in voyage_ids
        if event.event_type in {'LOAD', 'UNLOAD'}:
            assert event.voyage_id in voyage_ids


@pytest.mark.django_db(transaction=True)
def test_loaded_voyage_carrier_movement_schedules_are_ordered(tmp_path):
    _load_invariant_snapshot(tmp_path)

    for voyage in VoyageRecord.objects.all():
        movements = list(
            CarrierMovementRecord.objects.filter(voyage=voyage).order_by('departure_time', 'pk')
        )

        assert movements
        assert all(movement.departure_time < movement.arrival_time for movement in movements)
        assert all(
            previous.arrival_time <= following.departure_time
            and previous.arrival_location_id == following.departure_location_id
            for previous, following in itertools.pairwise(movements)
        )
