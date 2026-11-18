import csv
import hashlib
import json
from dataclasses import replace
from itertools import pairwise
from pathlib import Path

import pytest
from django.core.management import call_command

from cargotracker.cargo.domain.delivery import Delivery
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.models import HandlingEventRecord
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.models import LocationRecord
from cargotracker.voyage.infrastructure.models import CarrierMovementRecord, VoyageRecord

MAPPING = Path(__file__).resolve().parents[2] / '.migration' / 'data' / 'mapping.yaml'

SNAPSHOT_ROWS = {
    'LOCATION': (
        ['ID', 'UNLOCODE', 'NAME'],
        [
            ['101', 'USNYC', 'New York'],
            ['102', 'NLRTM', 'Rotterdam'],
            ['103', 'DEHAM', 'Hamburg'],
        ],
    ),
    'VOYAGE': (['ID', 'VOYAGE_NUMBER'], [['900', 'V001']]),
    'CARGO': (
        [
            'ID',
            'TRACKING_ID',
            'ORIGIN_ID',
            'SPEC_ORIGIN_ID',
            'SPEC_DESTINATION_ID',
            'SPEC_ARRIVAL_DEADLINE',
            'TRANSPORT_STATUS',
            'LAST_KNOWN_LOCATION_ID',
            'CURRENT_VOYAGE_ID',
            'MISDIRECTED',
            'ETA',
            'NEXT_EXPECTED_HANDLING_EVENT_TYPE',
            'NEXT_EXPECTED_LOCATION_ID',
            'NEXT_EXPECTED_VOYAGE_ID',
            'UNLOADED_AT_DEST',
            'ROUTING_STATUS',
            'CALCULATED_AT',
            'LAST_EVENT_ID',
        ],
        [
            [
                '13',
                'FIDELITY-0001',
                '101',
                '101',
                '103',
                '2026-12-30',
                'ONBOARD_CARRIER',
                '102',
                '900',
                'false',
                '2026-11-11',
                'UNLOAD',
                '103',
                '900',
                'false',
                'ROUTED',
                '2026-11-12T12:00:00Z',
                '74',
            ]
        ],
    ),
    'HANDLINGEVENT': (
        [
            'ID',
            'TYPE',
            'VOYAGE_ID',
            'LOCATION_ID',
            'COMPLETIONTIME',
            'REGISTRATION',
            'CARGO_ID',
        ],
        [
            ['71', 'RECEIVE', None, '101', '2026-11-07T10:00:00Z', '2026-11-07T10:01:00Z', '13'],
            ['72', 'LOAD', '900', '101', '2026-11-08T00:00:00Z', '2026-11-08T00:01:00Z', '13'],
            ['73', 'UNLOAD', '900', '102', '2026-11-09T00:00:00Z', '2026-11-09T00:01:00Z', '13'],
            ['74', 'LOAD', '900', '102', '2026-11-10T00:00:00Z', '2026-11-10T00:01:00Z', '13'],
        ],
    ),
    'LEG': (
        [
            'ID',
            'LOAD_TIME',
            'UNLOAD_TIME',
            'LOAD_LOCATION_ID',
            'UNLOAD_LOCATION_ID',
            'VOYAGE_ID',
            'CARGO_ID',
        ],
        [
            ['81', '2026-11-08T00:00:00Z', '2026-11-09T00:00:00Z', '101', '102', '900', '13'],
            ['82', '2026-11-10T00:00:00Z', '2026-11-11T00:00:00Z', '102', '103', '900', '13'],
        ],
    ),
    'CARRIER_MOVEMENT': (
        [
            'ID',
            'ARRIVAL_TIME',
            'DEPARTURE_TIME',
            'ARRIVAL_LOCATION_ID',
            'DEPARTURE_LOCATION_ID',
            'VOYAGE_ID',
        ],
        [
            ['91', '2026-11-09T00:00:00Z', '2026-11-08T00:00:00Z', '102', '101', '900'],
            ['92', '2026-11-11T00:00:00Z', '2026-11-10T00:00:00Z', '103', '102', '900'],
        ],
    ),
}


def _write_snapshot(directory):
    directory.mkdir()
    tables = {}
    for table, (header, rows) in SNAPSHOT_ROWS.items():
        path = directory / f'{table}.csv'
        with path.open('w', encoding='utf-8', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(header)
            writer.writerows([['\\N' if value is None else value for value in row] for row in rows])
        tables[table] = {
            'rows': len(rows),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    (directory / 'manifest.json').write_text(
        json.dumps({'null': '\\N', 'tables': tables}),
        encoding='utf-8',
    )


@pytest.fixture
def loaded_snapshot(tmp_path):
    snapshot = tmp_path / 'snapshot'
    _write_snapshot(snapshot)
    call_command('load_data_snapshot', snapshot=str(snapshot), mapping=str(MAPPING))


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_matches_its_handling_history(loaded_snapshot):
    cargos = DjangoCargoRepository().find_all()

    assert cargos
    for cargo in cargos:
        history = DjangoHandlingEventRepository().lookup_handling_history_of_cargo(
            TrackingId(cargo.tracking_id.value)
        )
        derived = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            calculated_at=cargo.delivery.calculated_at,
        )
        derived = replace(derived, last_event_id=history.most_recent_event_id)

        assert cargo.delivery == derived


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(loaded_snapshot):
    cargos = DjangoCargoRepository().find_all()

    assert cargos
    for cargo in cargos:
        legs = cargo.itinerary.legs
        assert all(
            previous.unload_location == following.load_location
            for previous, following in pairwise(legs)
        )

    assert len(cargos[0].itinerary.legs) == 2


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_events_reference_existing_voyages_and_locations(loaded_snapshot):
    location_ids = set(LocationRecord.objects.values_list('pk', flat=True))
    voyage_ids = set(VoyageRecord.objects.values_list('pk', flat=True))
    events = list(HandlingEventRecord.objects.all())

    assert events
    assert all(event.location_id in location_ids for event in events)
    assert all(event.voyage_id is None or event.voyage_id in voyage_ids for event in events)


@pytest.mark.django_db(transaction=True)
def test_loaded_carrier_movements_form_a_chronological_voyage_schedule(loaded_snapshot):
    voyages = list(VoyageRecord.objects.all())

    assert voyages
    for voyage in voyages:
        movements = list(
            CarrierMovementRecord.objects.filter(voyage=voyage).order_by('departure_time', 'pk')
        )
        assert all(movement.departure_time < movement.arrival_time for movement in movements)
        assert all(
            previous.arrival_time <= following.departure_time
            for previous, following in pairwise(movements)
        )

    assert CarrierMovementRecord.objects.filter(voyage=voyages[0]).count() == 2
