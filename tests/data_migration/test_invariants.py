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
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.cargo.infrastructure.models import CargoRecord
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository

pytestmark = pytest.mark.django_db(transaction=True)

FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MAPPING = REPOSITORY_ROOT / '.migration' / 'data' / 'mapping.yaml'


def _read_rows(snapshot, table):
    with (snapshot / f'{table}.csv').open(encoding='utf-8', newline='') as stream:
        return list(csv.DictReader(stream))


def _write_rows(snapshot, table, rows):
    path = snapshot / f'{table}.csv'
    with path.open(encoding='utf-8', newline='') as stream:
        fieldnames = csv.DictReader(stream).fieldnames
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


def _consistent_snapshot(snapshot):
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)
    cargo = _read_rows(snapshot, 'CARGO')[0]
    cargo.update(
        {
            'SPEC_DESTINATION_ID': '103',
            'TRANSPORT_STATUS': 'IN_PORT',
            'LAST_KNOWN_LOCATION_ID': '101',
            'CURRENT_VOYAGE_ID': r'\N',
            'MISDIRECTED': 'false',
            'ETA': '2026-11-12',
            'NEXT_EXPECTED_HANDLING_EVENT_TYPE': 'LOAD',
            'NEXT_EXPECTED_LOCATION_ID': '101',
            'NEXT_EXPECTED_VOYAGE_ID': '900',
            'UNLOADED_AT_DEST': 'false',
            'ROUTING_STATUS': 'ROUTED',
        }
    )
    _write_rows(snapshot, 'CARGO', [cargo])

    event = _read_rows(snapshot, 'HANDLINGEVENT')[0]
    event.update({'VOYAGE_ID': r'\N', 'LOCATION_ID': '101'})
    _write_rows(snapshot, 'HANDLINGEVENT', [event])

    _write_rows(
        snapshot,
        'LOCATION',
        _read_rows(snapshot, 'LOCATION') + [{'ID': '103', 'UNLOCODE': 'FIHEL', 'NAME': 'Helsinki'}],
    )
    _write_rows(
        snapshot,
        'VOYAGE',
        [{'ID': '900', 'VOYAGE_NUMBER': 'CM001'}],
    )
    _write_rows(
        snapshot,
        'LEG',
        _read_rows(snapshot, 'LEG')
        + [
            {
                'ID': '82',
                'LOAD_TIME': '2026-11-10T08:00:00Z',
                'UNLOAD_TIME': '2026-11-12T08:00:00Z',
                'LOAD_LOCATION_ID': '102',
                'UNLOAD_LOCATION_ID': '103',
                'VOYAGE_ID': '900',
                'CARGO_ID': '13',
            }
        ],
    )
    _write_rows(
        snapshot,
        'CARRIER_MOVEMENT',
        _read_rows(snapshot, 'CARRIER_MOVEMENT')
        + [
            {
                'ID': '92',
                'ARRIVAL_TIME': '2026-11-11T09:00:00Z',
                'DEPARTURE_TIME': '2026-11-10T09:00:00Z',
                'ARRIVAL_LOCATION_ID': '103',
                'DEPARTURE_LOCATION_ID': '102',
                'VOYAGE_ID': '900',
            }
        ],
    )


@pytest.fixture
def loaded_snapshot(tmp_path):
    snapshot = tmp_path / 'snapshot'
    _consistent_snapshot(snapshot)
    call_command(
        'load_data_snapshot',
        snapshot=str(snapshot),
        mapping=str(MAPPING),
    )
    return snapshot


def test_loaded_cargo_delivery_matches_its_handling_history(loaded_snapshot):
    cargos = DjangoCargoRepository()
    handling_events = DjangoHandlingEventRepository()

    for record in CargoRecord.objects.order_by('pk'):
        cargo = cargos.find(TrackingId(record.tracking_id))
        history = handling_events.lookup_handling_history_of_cargo(cargo.tracking_id)
        stored = cargo.delivery
        derived = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            stored.calculated_at,
        )

        assert stored.transport_status == derived.transport_status
        assert stored.last_known_location == derived.last_known_location
        assert stored.current_voyage == derived.current_voyage
        assert stored.misdirected == derived.misdirected
        assert (stored.eta.date() if stored.eta else None) == (
            derived.eta.date() if derived.eta else None
        )
        assert stored.next_expected_activity == derived.next_expected_activity
        assert stored.unloaded_at_destination == derived.unloaded_at_destination
        assert stored.routing_status == derived.routing_status
        assert stored.last_event_id == history.most_recent_event_id
