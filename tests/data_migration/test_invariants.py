import csv
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import shutil

import pytest
from django.core.management import call_command

from cargotracker.cargo.domain.delivery import Delivery
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.domain.repository import HandlingEventRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_SNAPSHOT = Path(__file__).parent / 'fixtures' / 'DM-05C'
MAPPING = ROOT / '.migration' / 'data' / 'mapping.yaml'


def _snapshot_with_consistent_delivery(tmp_path):
    snapshot = tmp_path / 'snapshot'
    shutil.copytree(FIXTURE_SNAPSHOT, snapshot)
    cargo_path = snapshot / 'CARGO.csv'
    with cargo_path.open(newline='', encoding='utf-8') as stream:
        reader = csv.DictReader(stream)
        fieldnames = reader.fieldnames
        rows = list(reader)
    rows[0].update(
        TRANSPORT_STATUS='IN_PORT',
        LAST_KNOWN_LOCATION_ID='102',
        CURRENT_VOYAGE_ID='\\N',
        MISDIRECTED='true',
        ETA='\\N',
        NEXT_EXPECTED_HANDLING_EVENT_TYPE='\\N',
        NEXT_EXPECTED_LOCATION_ID='\\N',
        NEXT_EXPECTED_VOYAGE_ID='\\N',
        UNLOADED_AT_DEST='false',
        ROUTING_STATUS='ROUTED',
        LAST_EVENT_ID='71',
    )
    with cargo_path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    event_path = snapshot / 'HANDLINGEVENT.csv'
    with event_path.open(newline='', encoding='utf-8') as stream:
        reader = csv.DictReader(stream)
        fieldnames = reader.fieldnames
        rows = list(reader)
    rows[0]['VOYAGE_ID'] = '\\N'
    with event_path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    manifest_path = snapshot / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for table in ('CARGO', 'HANDLINGEVENT'):
        path = snapshot / f'{table}.csv'
        with path.open(newline='', encoding='utf-8') as stream:
            row_count = sum(1 for _ in csv.DictReader(stream))
        manifest['tables'][table].update(
            rows=row_count,
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        )
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
    return snapshot


@pytest.mark.django_db(transaction=True)
def test_loaded_cargo_delivery_matches_its_handling_history(tmp_path):
    snapshot = _snapshot_with_consistent_delivery(tmp_path)
    call_command(
        'load_data_snapshot',
        snapshot=str(snapshot),
        mapping=str(MAPPING),
    )
    cargos = DjangoCargoRepository().find_all()
    events: HandlingEventRepository = DjangoHandlingEventRepository()

    for cargo in cargos:
        history = events.lookup_handling_history_of_cargo(cargo.tracking_id)
        derived = Delivery.derived_from(
            cargo.route_specification,
            cargo.itinerary,
            history,
            calculated_at=cargo.delivery.calculated_at,
        )

        assert replace(derived, last_event_id=history.most_recent_event_id) == cargo.delivery
