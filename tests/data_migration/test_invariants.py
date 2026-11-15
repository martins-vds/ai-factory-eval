import csv
import hashlib
import json
import shutil
from datetime import UTC, datetime
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
MAPPING = Path(__file__).parents[2] / '.migration' / 'data' / 'mapping.yaml'


def _replace_rows(snapshot, table, rows):
    path = snapshot / f'{table}.csv'
    with path.open(newline='', encoding='utf-8') as stream:
        header = next(csv.reader(stream))
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(header)
        writer.writerows(rows)

    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest['tables'][table].update(
        rows=len(rows),
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
    )
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')


def _load_fixture(tmp_path):
    snapshot = tmp_path / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)
    _replace_rows(
        snapshot,
        'LOCATION',
        [
            ['4', 'USNYC', 'New York'],
            ['5', 'NLRTM', 'Rotterdam'],
            ['6', 'DEHAM', 'Hamburg'],
        ],
    )
    _replace_rows(snapshot, 'VOYAGE', [['9', 'V001']])
    _replace_rows(
        snapshot,
        'CARGO',
        [
            [
                '15',
                'ABC123',
                '4',
                '4',
                '5',
                '2026-11-15',
                'ONBOARD_CARRIER',
                '4',
                '9',
                'false',
                '2026-11-08',
                'UNLOAD',
                '6',
                '9',
                'false',
                'ROUTED',
                '2026-11-07T04:05:06Z',
                '35',
            ]
        ],
    )
    _replace_rows(
        snapshot,
        'HANDLINGEVENT',
        [['35', 'LOAD', '9', '4', '2026-11-07T10:30:00Z', '2026-11-07T10:31:00Z', '15']],
    )
    _replace_rows(
        snapshot,
        'LEG',
        [
            ['50', '2026-11-07T10:00:00Z', '2026-11-07T12:00:00Z', '4', '6', '9', '15'],
            ['51', '2026-11-07T13:00:00Z', '2026-11-08T12:00:00Z', '6', '5', '9', '15'],
        ],
    )
    _replace_rows(
        snapshot,
        'CARRIER_MOVEMENT',
        [
            ['55', '2026-11-07T12:00:00Z', '2026-11-07T10:00:00Z', '6', '4', '9'],
            ['56', '2026-11-08T12:00:00Z', '2026-11-07T13:00:00Z', '5', '6', '9'],
        ],
    )
    call_command('load_data_snapshot', snapshot=str(snapshot), mapping=str(MAPPING))


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_matches_its_handling_history(tmp_path):
    _load_fixture(tmp_path)
    cargo = DjangoCargoRepository().find(TrackingId('ABC123'))
    history = DjangoHandlingEventRepository().lookup_handling_history_of_cargo(
        TrackingId('ABC123')
    )

    assert history.most_recent_event is not None
    expected = Delivery.derived_from(
        cargo.route_specification,
        cargo.itinerary,
        history,
        calculated_at=datetime(2026, 11, 7, 4, 5, 6, tzinfo=UTC),
    )

    assert cargo.delivery.transport_status == expected.transport_status
    assert cargo.delivery.last_known_location == expected.last_known_location
    assert cargo.delivery.current_voyage == expected.current_voyage
    assert cargo.delivery.misdirected == expected.misdirected
    assert cargo.delivery.eta.date() == expected.eta.date()
    assert cargo.delivery.next_expected_activity == expected.next_expected_activity
    assert cargo.delivery.unloaded_at_destination == expected.unloaded_at_destination
    assert cargo.delivery.routing_status == expected.routing_status
    assert cargo.delivery.calculated_at == expected.calculated_at
    assert cargo.delivery.last_event_id == history.most_recent_event_id


@pytest.mark.django_db(transaction=True)
def test_loaded_itinerary_legs_connect(tmp_path):
    _load_fixture(tmp_path)

    cargo_ids = list(CargoRecord.objects.values_list('pk', flat=True))
    assert cargo_ids
    for cargo_id in cargo_ids:
        legs = list(LegRecord.objects.filter(cargo_id=cargo_id).order_by('load_time', 'pk'))
        assert legs
        assert all(
            previous.unload_location_id == following.load_location_id
            for previous, following in zip(legs, legs[1:], strict=False)
        )
    assert any(LegRecord.objects.filter(cargo_id=cargo_id).count() > 1 for cargo_id in cargo_ids)


@pytest.mark.django_db(transaction=True)
def test_loaded_handling_events_reference_existing_voyages_and_locations(tmp_path):
    _load_fixture(tmp_path)

    events = list(HandlingEventRecord.objects.all())
    voyage_ids = set(VoyageRecord.objects.values_list('pk', flat=True))
    location_ids = set(LocationRecord.objects.values_list('pk', flat=True))

    assert events
    assert all(event.voyage_id in voyage_ids for event in events)
    assert all(event.location_id in location_ids for event in events)


@pytest.mark.django_db(transaction=True)
def test_loaded_carrier_movement_schedules_are_in_order(tmp_path):
    _load_fixture(tmp_path)

    voyages = list(VoyageRecord.objects.all())
    schedules = [
        list(
            CarrierMovementRecord.objects.filter(voyage_id=voyage.pk).order_by(
                'departure_time', 'pk'
            )
        )
        for voyage in voyages
    ]

    assert voyages
    assert any(len(schedule) > 1 for schedule in schedules)
    for schedule in schedules:
        assert all(movement.departure_time < movement.arrival_time for movement in schedule)
        assert all(
            previous.arrival_time <= following.departure_time
            for previous, following in zip(schedule, schedule[1:], strict=False)
        )
