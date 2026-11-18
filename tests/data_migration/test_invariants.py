import csv
import hashlib
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
MAPPING = Path(__file__).parents[2] / '.migration' / 'data' / 'mapping.yaml'


def _update_table(snapshot, table, transform):
    path = snapshot / f'{table}.csv'
    with path.open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        rows = list(reader)

    transform(rows)

    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    return rows, path


def _load_invariant_fixture(tmp_path):
    snapshot = tmp_path / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)

    changes = {
        'LOCATION': lambda rows: rows.append(
            {'ID': '103', 'UNLOCODE': 'SGSIN', 'NAME': 'Singapore'}
        ),
        'CARGO': lambda rows: rows[0].update(
            {
                'SPEC_DESTINATION_ID': '103',
                'TRANSPORT_STATUS': 'IN_PORT',
                'LAST_KNOWN_LOCATION_ID': '102',
                'CURRENT_VOYAGE_ID': '\\N',
                'MISDIRECTED': 'false',
                'ETA': '2026-11-11',
                'NEXT_EXPECTED_HANDLING_EVENT_TYPE': '\\N',
                'NEXT_EXPECTED_LOCATION_ID': '\\N',
                'NEXT_EXPECTED_VOYAGE_ID': '\\N',
                'UNLOADED_AT_DEST': 'false',
                'ROUTING_STATUS': 'ROUTED',
                'LAST_EVENT_ID': '72',
            }
        ),
        'HANDLINGEVENT': lambda rows: (
            rows[0].update({'TYPE': 'LOAD', 'LOCATION_ID': '101'}),
            rows.append(
                {
                    'ID': '72',
                    'TYPE': 'CUSTOMS',
                    'VOYAGE_ID': '\\N',
                    'LOCATION_ID': '102',
                    'COMPLETIONTIME': '2026-11-07T11:00:00Z',
                    'REGISTRATION': '2026-11-07T11:01:00Z',
                    'CARGO_ID': '13',
                }
            ),
        ),
        'LEG': lambda rows: rows.append(
            {
                'ID': '82',
                'LOAD_TIME': '2026-11-10T08:00:00Z',
                'UNLOAD_TIME': '2026-11-11T11:00:00Z',
                'LOAD_LOCATION_ID': '102',
                'UNLOAD_LOCATION_ID': '103',
                'VOYAGE_ID': '900',
                'CARGO_ID': '13',
            }
        ),
        'CARRIER_MOVEMENT': lambda rows: (
            rows[0].update(
                {
                    'DEPARTURE_TIME': '2026-11-08T08:00:00Z',
                    'ARRIVAL_TIME': '2026-11-09T13:00:00+02:00',
                }
            ),
            rows.append(
                {
                    'ID': '92',
                    'ARRIVAL_TIME': '2026-11-11T11:00:00Z',
                    'DEPARTURE_TIME': '2026-11-10T08:00:00Z',
                    'ARRIVAL_LOCATION_ID': '103',
                    'DEPARTURE_LOCATION_ID': '102',
                    'VOYAGE_ID': '900',
                }
            ),
        ),
    }

    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for table, transform in changes.items():
        rows, path = _update_table(snapshot, table, transform)
        manifest['tables'][table].update(
            rows=len(rows),
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        )
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')

    call_command(
        'load_data_snapshot',
        snapshot=str(snapshot),
        mapping=str(MAPPING),
    )


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_matches_derived_state_and_handling_history(tmp_path):
    _load_invariant_fixture(tmp_path)
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
            cargo.delivery.calculated_at,
        )
        derived = replace(derived, last_event_id=history.most_recent_event_id)

        stored_eta = cargo.delivery.eta.date() if cargo.delivery.eta is not None else None
        derived_eta = derived.eta.date() if derived.eta is not None else None
        assert stored_eta == derived_eta
        assert replace(cargo.delivery, eta=derived.eta) == derived
        assert cargo.delivery.last_event_id == history.most_recent_event_id


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(tmp_path):
    _load_invariant_fixture(tmp_path)

    cargos = DjangoCargoRepository().find_all()
    assert cargos
    assert any(len(cargo.itinerary.legs) > 1 for cargo in cargos)
    for cargo in cargos:
        for previous, following in zip(cargo.itinerary.legs, cargo.itinerary.legs[1:]):
            assert previous.unload_location == following.load_location


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_events_reference_existing_voyages_and_locations(tmp_path):
    _load_invariant_fixture(tmp_path)

    events = list(HandlingEventRecord.objects.all())
    voyage_ids = set(VoyageRecord.objects.values_list('pk', flat=True))
    location_ids = set(LocationRecord.objects.values_list('pk', flat=True))

    assert events
    assert any(event.voyage_id is None for event in events)
    for event in events:
        assert event.voyage_id is None or event.voyage_id in voyage_ids
        assert event.location_id in location_ids


@pytest.mark.django_db(transaction=True)
def test_loaded_voyage_carrier_movements_are_in_schedule_order(tmp_path):
    _load_invariant_fixture(tmp_path)

    voyages = VoyageRecord.objects.all()
    assert voyages.exists()
    assert CarrierMovementRecord.objects.count() > 1
    for voyage in voyages:
        movements = list(
            CarrierMovementRecord.objects.filter(voyage=voyage).order_by('departure_time', 'pk')
        )
        for index, movement in enumerate(movements):
            assert movement.departure_time <= movement.arrival_time
            if index:
                previous = movements[index - 1]
                assert previous.arrival_time <= movement.departure_time
                assert previous.arrival_location_id == movement.departure_location_id
