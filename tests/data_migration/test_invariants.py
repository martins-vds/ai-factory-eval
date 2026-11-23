import csv
import hashlib
import json
import shutil
from collections import defaultdict
from itertools import pairwise
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
from cargotracker.voyage.infrastructure.models import (
    CarrierMovementRecord,
    VoyageRecord,
)

FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MAPPING = REPOSITORY_ROOT / '.migration' / 'data' / 'mapping.yaml'


def _read_rows(snapshot, table):
    with (snapshot / f'{table}.csv').open(encoding='utf-8', newline='') as source:
        return list(csv.DictReader(source))


def _write_rows(snapshot, table, rows):
    path = snapshot / f'{table}.csv'
    with path.open('w', encoding='utf-8', newline='') as target:
        writer = csv.DictWriter(target, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest['tables'][table].update(
        rows=len(rows),
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
    )
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')


def _prepare_snapshot(tmp_path):
    snapshot = tmp_path / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)

    locations = _read_rows(snapshot, 'LOCATION')
    locations.append({'ID': '103', 'UNLOCODE': 'BEANR', 'NAME': 'Antwerp'})
    _write_rows(snapshot, 'LOCATION', locations)

    cargo = _read_rows(snapshot, 'CARGO')[0]
    cargo.update(
        TRANSPORT_STATUS='ONBOARD_CARRIER',
        LAST_KNOWN_LOCATION_ID='101',
        CURRENT_VOYAGE_ID='900',
        MISDIRECTED='false',
        ETA='2026-11-09',
        NEXT_EXPECTED_HANDLING_EVENT_TYPE='UNLOAD',
        NEXT_EXPECTED_LOCATION_ID='103',
        NEXT_EXPECTED_VOYAGE_ID='900',
        UNLOADED_AT_DEST='false',
        ROUTING_STATUS='ROUTED',
        CALCULATED_AT='2026-11-08T10:02:00Z',
        LAST_EVENT_ID='72',
    )
    _write_rows(snapshot, 'CARGO', [cargo])

    events = _read_rows(snapshot, 'HANDLINGEVENT')
    receive = events[0]
    receive.update(
        ID='71',
        VOYAGE_ID=r'\N',
        LOCATION_ID='101',
        COMPLETIONTIME='2026-11-07T10:12:13+02:00',
        REGISTRATION='2026-11-07T10:13:14Z',
    )
    load = dict(receive)
    load.update(
        ID='72',
        TYPE='LOAD',
        VOYAGE_ID='900',
        COMPLETIONTIME='2026-11-08T10:00:00Z',
        REGISTRATION='2026-11-08T10:01:00Z',
    )
    _write_rows(snapshot, 'HANDLINGEVENT', [receive, load])

    legs = _read_rows(snapshot, 'LEG')
    first_leg = legs[0]
    first_leg.update(
        LOAD_TIME='2026-11-08T11:00:00Z',
        UNLOAD_TIME='2026-11-08T14:00:00Z',
        LOAD_LOCATION_ID='101',
        UNLOAD_LOCATION_ID='103',
    )
    second_leg = dict(first_leg)
    second_leg.update(
        ID='82',
        LOAD_TIME='2026-11-08T15:00:00Z',
        UNLOAD_TIME='2026-11-09T11:00:00Z',
        LOAD_LOCATION_ID='103',
        UNLOAD_LOCATION_ID='102',
    )
    _write_rows(snapshot, 'LEG', [first_leg, second_leg])

    movements = _read_rows(snapshot, 'CARRIER_MOVEMENT')
    second_movement = movements[0]
    second_movement.update(
        DEPARTURE_TIME='2026-11-08T15:00:00Z',
        ARRIVAL_TIME='2026-11-09T11:00:00Z',
        DEPARTURE_LOCATION_ID='103',
        ARRIVAL_LOCATION_ID='102',
    )
    first_movement = dict(second_movement)
    first_movement.update(
        ID='90',
        DEPARTURE_TIME='2026-11-08T11:00:00Z',
        ARRIVAL_TIME='2026-11-08T14:00:00Z',
        DEPARTURE_LOCATION_ID='101',
        ARRIVAL_LOCATION_ID='103',
    )
    _write_rows(snapshot, 'CARRIER_MOVEMENT', [first_movement, second_movement])
    return snapshot


@pytest.mark.django_db(transaction=True)
def test_loaded_snapshot_preserves_business_invariants(tmp_path):
    snapshot = _prepare_snapshot(tmp_path)
    call_command('load_data_snapshot', snapshot=str(snapshot), mapping=str(MAPPING))

    cargo = DjangoCargoRepository().find(TrackingId('FIDELITY-0001'))
    assert cargo is not None
    history = DjangoHandlingEventRepository().lookup_handling_history_of_cargo(cargo.tracking_id)
    assert history.most_recent_event_id == cargo.delivery.last_event_id
    derived = Delivery.derived_from(
        cargo.route_specification,
        cargo.itinerary,
        history,
        cargo.delivery.calculated_at,
    )
    assert cargo.delivery.transport_status == derived.transport_status
    assert cargo.delivery.last_known_location == derived.last_known_location
    assert cargo.delivery.current_voyage == derived.current_voyage
    assert cargo.delivery.misdirected == derived.misdirected
    assert (cargo.delivery.eta.date() if cargo.delivery.eta else None) == (
        derived.eta.date() if derived.eta else None
    )
    assert cargo.delivery.next_expected_activity == derived.next_expected_activity
    assert cargo.delivery.unloaded_at_destination == derived.unloaded_at_destination
    assert cargo.delivery.routing_status == derived.routing_status
    assert cargo.delivery.calculated_at == derived.calculated_at

    cargo_records = CargoRecord.objects.all()
    assert cargo_records.exists()
    for cargo_record in cargo_records:
        legs = list(LegRecord.objects.filter(cargo=cargo_record).order_by('load_time', 'pk'))
        assert legs
        assert all(
            previous.unload_location_id == following.load_location_id
            for previous, following in pairwise(legs)
        )
    assert (
        max(LegRecord.objects.filter(cargo=cargo_record).count() for cargo_record in cargo_records)
        > 1
    )

    events = list(HandlingEventRecord.objects.order_by('pk'))
    assert events
    for event in events:
        assert LocationRecord.objects.filter(pk=event.location_id).exists()
        if event.event_type in {'LOAD', 'UNLOAD'}:
            assert event.voyage_id is not None
        if event.voyage_id is not None:
            assert VoyageRecord.objects.filter(pk=event.voyage_id).exists()

    movements_by_voyage = defaultdict(list)
    for movement in CarrierMovementRecord.objects.order_by('voyage_id', 'departure_time', 'pk'):
        movements_by_voyage[movement.voyage_id].append(movement)
    assert movements_by_voyage
    assert max(map(len, movements_by_voyage.values())) > 1
    for movements in movements_by_voyage.values():
        for movement in movements:
            assert movement.departure_time < movement.arrival_time
        for previous, following in pairwise(movements):
            assert previous.arrival_time <= following.departure_time
            assert previous.arrival_location_id == following.departure_location_id
