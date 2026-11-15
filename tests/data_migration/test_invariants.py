import csv
import hashlib
import itertools
import json
import shutil
from pathlib import Path

import pytest
import yaml
from django.core.management import call_command
from test_load import MAPPING

from cargotracker.cargo.domain.delivery import Delivery
from cargotracker.cargo.infrastructure.models import CargoRecord
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.models import HandlingEventRecord
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.models import LocationRecord
from cargotracker.voyage.infrastructure.models import CarrierMovementRecord, VoyageRecord

FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'


def _rewrite_table(snapshot, table, updates=None, additions=()):
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

    _rewrite_table(
        snapshot, 'LOCATION', additions=[{'ID': '103', 'UNLOCODE': 'DKCPH', 'NAME': 'Copenhagen'}]
    )
    _rewrite_table(snapshot, 'VOYAGE', additions=[{'ID': '901', 'VOYAGE_NUMBER': 'V-901'}])
    _rewrite_table(
        snapshot,
        'CARGO',
        updates={
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
                'LAST_EVENT_ID': '71',
            }
        },
    )
    _rewrite_table(
        snapshot,
        'HANDLINGEVENT',
        updates={'71': {'TYPE': 'LOAD', 'VOYAGE_ID': '900', 'LOCATION_ID': '101'}},
    )
    _rewrite_table(
        snapshot,
        'LEG',
        additions=[
            {
                'ID': '82',
                'LOAD_TIME': '2026-11-09T12:00:00Z',
                'UNLOAD_TIME': '2026-11-10T11:00:00Z',
                'LOAD_LOCATION_ID': '102',
                'UNLOAD_LOCATION_ID': '103',
                'VOYAGE_ID': '901',
                'CARGO_ID': '13',
            }
        ],
    )
    _rewrite_table(
        snapshot,
        'CARRIER_MOVEMENT',
        additions=[
            {
                'ID': '92',
                'ARRIVAL_TIME': '2026-11-09T18:00:00Z',
                'DEPARTURE_TIME': '2026-11-09T11:00:00Z',
                'ARRIVAL_LOCATION_ID': '102',
                'DEPARTURE_LOCATION_ID': '101',
                'VOYAGE_ID': '900',
            },
            {
                'ID': '93',
                'ARRIVAL_TIME': '2026-11-10T10:00:00Z',
                'DEPARTURE_TIME': '2026-11-09T12:00:00Z',
                'ARRIVAL_LOCATION_ID': '103',
                'DEPARTURE_LOCATION_ID': '102',
                'VOYAGE_ID': '901',
            },
            {
                'ID': '94',
                'ARRIVAL_TIME': '2026-11-10T18:00:00Z',
                'DEPARTURE_TIME': '2026-11-10T11:00:00Z',
                'ARRIVAL_LOCATION_ID': '101',
                'DEPARTURE_LOCATION_ID': '103',
                'VOYAGE_ID': '901',
            },
        ],
    )

    mapping = tmp_path / 'mapping.yaml'
    mapping.write_text(yaml.safe_dump(MAPPING), encoding='utf-8')
    call_command('load_data_snapshot', snapshot=str(snapshot), mapping=str(mapping))


@pytest.fixture
def loaded_snapshot(tmp_path):
    _load_snapshot(tmp_path)


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_state_matches_handling_history(loaded_snapshot):
    cargos = DjangoCargoRepository()
    handling_events = DjangoHandlingEventRepository()
    loaded_cargos = cargos.find_all()
    assert loaded_cargos

    for cargo in loaded_cargos:
        history = handling_events.lookup_handling_history_of_cargo(cargo.tracking_id)
        derived = Delivery.derived_from(cargo.route_specification, cargo.itinerary, history)
        stored = cargo.delivery

        assert stored.transport_status == derived.transport_status
        assert stored.last_known_location == derived.last_known_location
        assert stored.current_voyage == derived.current_voyage
        assert stored.misdirected == derived.misdirected
        stored_eta = stored.eta.date() if stored.eta is not None else None
        derived_eta = derived.eta.date() if derived.eta is not None else None
        assert stored_eta == derived_eta
        assert stored.next_expected_activity == derived.next_expected_activity
        assert stored.unloaded_at_destination == derived.unloaded_at_destination
        assert stored.routing_status == derived.routing_status
        assert stored.last_event_id == history.most_recent_event_id


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(loaded_snapshot):
    cargos = list(CargoRecord.objects.all())
    assert cargos

    for cargo in cargos:
        legs = list(cargo.legs.order_by('load_time', 'pk'))
        assert len(legs) > 1
        assert all(
            current.unload_location_id == following.load_location_id
            for current, following in itertools.pairwise(legs)
        )


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_events_reference_existing_voyages_and_locations(loaded_snapshot):
    events = list(HandlingEventRecord.objects.all())
    assert events

    for event in events:
        assert LocationRecord.objects.filter(pk=event.location_id).exists()
        if event.voyage_id is not None:
            assert VoyageRecord.objects.filter(pk=event.voyage_id).exists()


@pytest.mark.django_db(transaction=True)
def test_loaded_carrier_movement_schedules_are_in_order(loaded_snapshot):
    voyages = list(VoyageRecord.objects.all())
    assert voyages
    schedules = [
        list(CarrierMovementRecord.objects.filter(voyage=voyage).order_by('departure_time', 'pk'))
        for voyage in voyages
    ]
    assert any(len(movements) > 1 for movements in schedules)

    for movements in schedules:
        assert all(movement.departure_time <= movement.arrival_time for movement in movements)
        assert all(
            previous.arrival_time <= following.departure_time
            for previous, following in itertools.pairwise(movements)
        )
