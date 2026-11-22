from django.core.management import call_command
from django.template.loader import render_to_string

import pytest

from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository


@pytest.mark.django_db
def test_not_routed_table_opens_destination_and_deadline_dialogs():
    call_command('seed_sample_data')
    cargo = DjangoCargoRepository().find(TrackingId('DEF789'))
    assert cargo is not None

    content = render_to_string(
        'booking/dashboard/not_routed_table.html',
        {'not_routed_cargos': [cargo]},
    )

    assert 'Change destination' in content
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in content
    assert 'Change deadline' in content
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in content
    assert 'hx-target="#cargo-edit-dialog"' in content
