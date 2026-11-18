import re
from datetime import UTC, datetime

import pytest
from django.core.management import call_command
from django.test import RequestFactory

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.booking.interfaces.dialogs.views import create_booking_dialog_views
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository


def _create_dialog_views(locations):
    cargo_repository = DjangoCargoRepository()
    return create_booking_dialog_views(
        CargoDashboard(cargo_repository),
        CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
        lambda: locations,
    )


@pytest.mark.django_db
def test_destination_dialog_shows_current_specification_and_stable_filtered_options():
    call_command('seed_sample_data')
    backing_locations = DjangoLocationRepository().find_all()
    change_destination, _ = _create_dialog_views(backing_locations)
    request = RequestFactory().get('/admin/cargo/DEF789/destination/')

    first_response = change_destination(request, 'DEF789')
    second_response = change_destination(request, 'DEF789')
    first_content = first_response.content.decode()
    second_content = second_response.content.decode()
    options = re.search(
        r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', first_content, re.DOTALL
    )

    assert first_response.status_code == 200
    assert 'Hong Kong' in first_content and 'CNHKG' in first_content
    assert 'Melbourne' in first_content and 'AUMEL' in first_content
    assert 'value="2024-02-29"' in first_content
    assert options is not None
    assert 'value="CNHKG"' not in options.group(1)
    assert 'value="AUMEL"' not in options.group(1)
    assert options.group(1).count('<option') == len(backing_locations) - 2
    assert first_content == second_content
    assert len(backing_locations) == 13
    assert backing_locations == DjangoLocationRepository().find_all()
