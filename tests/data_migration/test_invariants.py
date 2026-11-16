import csv
import hashlib
import json
import shutil
from dataclasses import replace
from pathlib import Path

import pytest
from django.core.management import call_command

from cargotracker.cargo.domain.delivery import Delivery
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository

FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = Path(__file__).resolve().parents[2] / '.migration' / 'data' / 'mapping.yaml'

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def loaded_snapshot(tmp_path):
    snapshot = tmp_path / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)
    _make_delivery_consistent(snapshot)
    _refresh_manifest(snapshot)
    call_command(
        'load_data_snapshot',
        snapshot=str(snapshot),
        mapping=str(MAPPING),
    )


def _read_table(snapshot, table):
    with (snapshot / f'{table}.csv').open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def _write_table(snapshot, table, fieldnames, rows):
    with (snapshot / f'{table}.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _make_delivery_consistent(snapshot):
    fields, cargos = _read_table(snapshot, 'CARGO')
    cargo = cargos[0]
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
        LAST_EVENT_ID='71',
    )
    _write_table(snapshot, 'CARGO', fields, cargos)

    fields, events = _read_table(snapshot, 'HANDLINGEVENT')
    events[0].update(TYPE='RECEIVE', VOYAGE_ID=r'\N', LOCATION_ID='101')
    _write_table(snapshot, 'HANDLINGEVENT', fields, events)


def _refresh_manifest(snapshot):
    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for path in snapshot.glob('*.csv'):
        fields, rows = _read_table(snapshot, path.stem)
        manifest['tables'][path.stem] = {
            'rows': len(rows),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')


def test_loaded_cargo_delivery_matches_its_handling_history(loaded_snapshot):
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
        if derived.eta is not None:
            derived = replace(derived, eta=derived.eta.replace(hour=0, minute=0, second=0, microsecond=0))

        assert replace(derived, last_event_id=history.most_recent_event_id) == cargo.delivery
