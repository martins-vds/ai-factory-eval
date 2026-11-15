import csv
import hashlib
import json
from dataclasses import replace
from pathlib import Path

import pytest
from django.core.management import call_command

from cargotracker.cargo.domain.delivery import Delivery
from cargotracker.cargo.infrastructure.models import CargoRecord, LegRecord
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.models import HandlingEventRecord
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.models import LocationRecord
from cargotracker.voyage.infrastructure.models import CarrierMovementRecord, VoyageRecord

PROJECT_ROOT = Path(__file__).parents[2]
MAPPING = PROJECT_ROOT / '.migration' / 'data' / 'mapping.yaml'

SNAPSHOT_TABLES = {
    'LOCATION': (
        ['ID', 'UNLOCODE', 'NAME'],
        [
            ['101', 'USNYC', 'New York'],
            ['102', 'NLRTM', 'Rotterdam'],
            ['103', 'USDAL', 'Dallas'],
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
                '101',
                '900',
                'false',
                '2026-11-10',
                'UNLOAD',
                '102',
                '900',
                'false',
                'ROUTED',
                '2026-11-08T11:00:00Z',
                '71',
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
        [['71', 'LOAD', '900', '101', '2026-11-08T10:00:00Z', '2026-11-08T10:01:00Z', '13']],
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
            ['81', '2026-11-08T10:00:00Z', '2026-11-09T10:00:00Z', '101', '102', '900', '13'],
            ['82', '2026-11-09T10:00:00Z', '2026-11-10T10:00:00Z', '102', '103', '900', '13'],
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
            ['91', '2026-11-09T10:00:00Z', '2026-11-08T10:00:00Z', '102', '101', '900'],
            ['92', '2026-11-10T10:00:00Z', '2026-11-09T10:00:00Z', '103', '102', '900'],
        ],
    ),
}


def _write_snapshot(snapshot):
    snapshot.mkdir()
    tables = {}
    for table, (header, rows) in SNAPSHOT_TABLES.items():
        path = snapshot / f'{table}.csv'
        with path.open('w', encoding='utf-8', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(header)
            writer.writerows(rows)
        tables[table] = {
            'rows': len(rows),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    (snapshot / 'manifest.json').write_text(
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
    cargo_repository = DjangoCargoRepository()
    handling_repository = DjangoHandlingEventRepository()

    for cargo in cargo_repository.find_all():
        history = handling_repository.lookup_handling_history_of_cargo(cargo.tracking_id)
        derived = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            calculated_at=cargo.delivery.calculated_at,
        )
        if derived.eta is not None:
            derived = replace(
                derived,
                eta=derived.eta.replace(hour=0, minute=0, second=0, microsecond=0),
            )

        assert replace(derived, last_event_id=history.most_recent_event_id) == cargo.delivery


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(loaded_snapshot):
    for cargo in CargoRecord.objects.all():
        legs = list(LegRecord.objects.filter(cargo=cargo).order_by('load_time', 'pk'))

        assert all(
            previous.unload_location_id == following.load_location_id
            for previous, following in zip(legs, legs[1:])
        )


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_events_reference_existing_voyages_and_locations(loaded_snapshot):
    location_ids = set(LocationRecord.objects.values_list('pk', flat=True))
    voyage_ids = set(VoyageRecord.objects.values_list('pk', flat=True))

    for event in HandlingEventRecord.objects.all():
        assert event.location_id in location_ids
        assert event.voyage_id is None or event.voyage_id in voyage_ids


@pytest.mark.django_db(transaction=True)
def test_loaded_voyage_carrier_movements_form_ordered_schedules(loaded_snapshot):
    for voyage in VoyageRecord.objects.all():
        movements = list(
            CarrierMovementRecord.objects.filter(voyage=voyage).order_by('departure_time', 'pk')
        )

        assert all(
            previous.arrival_time <= following.departure_time
            and previous.arrival_location_id == following.departure_location_id
            for previous, following in zip(movements, movements[1:])
        )
