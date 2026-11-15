import csv
import hashlib
import json
import shutil
from pathlib import Path

import pytest
from django.core.management import call_command

from cargotracker.cargo.domain.delivery import Delivery
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository

FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = Path(__file__).resolve().parents[2] / '.migration' / 'data' / 'mapping.yaml'


def _read_table(snapshot, table):
    with (snapshot / f'{table}.csv').open(encoding='utf-8', newline='') as source:
        reader = csv.DictReader(source)
        return reader.fieldnames, list(reader)


def _write_tables(snapshot, tables):
    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for table, (fieldnames, rows) in tables.items():
        path = snapshot / f'{table}.csv'
        with path.open('w', encoding='utf-8', newline='') as target:
            writer = csv.DictWriter(target, fieldnames=fieldnames, lineterminator='\n')
            writer.writeheader()
            writer.writerows(rows)
        manifest['tables'][table] = {
            'rows': len(rows),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')


def _consistent_snapshot(snapshot):
    tables = {table: _read_table(snapshot, table) for table in ('CARGO', 'HANDLINGEVENT')}
    cargo = tables['CARGO'][1][0]
    cargo.update(
        TRANSPORT_STATUS='IN_PORT',
        LAST_KNOWN_LOCATION_ID='101',
        CURRENT_VOYAGE_ID=r'\N',
        MISDIRECTED='false',
        ETA='2026-11-09',
        NEXT_EXPECTED_HANDLING_EVENT_TYPE='LOAD',
        NEXT_EXPECTED_LOCATION_ID='101',
        NEXT_EXPECTED_VOYAGE_ID='900',
        UNLOADED_AT_DEST='false',
        ROUTING_STATUS='ROUTED',
    )
    event = tables['HANDLINGEVENT'][1][0]
    event.update(
        VOYAGE_ID=r'\N',
        LOCATION_ID='101',
        COMPLETIONTIME='2026-11-07T10:12:13Z',
        REGISTRATION='2026-11-07T10:13:14Z',
    )
    _write_tables(snapshot, tables)


@pytest.fixture
def loaded_snapshot(tmp_path):
    snapshot = tmp_path / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)
    _consistent_snapshot(snapshot)
    call_command('load_data_snapshot', snapshot=str(snapshot), mapping=str(MAPPING))


def _delivery_state(delivery):
    return (
        delivery.transport_status,
        delivery.last_known_location,
        delivery.current_voyage,
        delivery.misdirected,
        delivery.eta.date() if delivery.eta is not None else None,
        delivery.next_expected_activity,
        delivery.unloaded_at_destination,
        delivery.routing_status,
    )


@pytest.mark.django_db
def test_loaded_cargo_delivery_state_matches_its_handling_history(loaded_snapshot):
    repository = DjangoCargoRepository()
    history_repository = DjangoHandlingEventRepository()
    cargos = repository.find_all()
    assert cargos

    for cargo in cargos:
        history = history_repository.lookup_handling_history_of_cargo(cargo.tracking_id)
        derived = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            cargo.delivery.calculated_at,
        )

        assert _delivery_state(derived) == _delivery_state(cargo.delivery)
        assert cargo.delivery.last_event_id == history.most_recent_event_id
