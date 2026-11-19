import re
from types import SimpleNamespace

import pytest
from django.core.management import call_command
from django.test import RequestFactory

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.booking.interfaces.dialogs.views import create_booking_dialog_views
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository


@pytest.mark.django_db
def test_destination_dialog_excludes_origin_and_current_destination_without_mutating_locations():
    call_command('seed_sample_data')
    cargo_repository = DjangoCargoRepository()
    location_repository = DjangoLocationRepository()
    locations = location_repository.find_all()
    original_locations = locations.copy()
    destination_view, _ = create_booking_dialog_views(
        CargoDashboard(cargo_repository),
        CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
        lambda: locations,
    )
    request = RequestFactory().get('/admin/cargo/DEF789/destination/')
    request.user = SimpleNamespace(is_authenticated=False)

    response = destination_view(request, 'DEF789')
    content = response.content.decode()
    options = re.search(r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', content, re.DOTALL)

    assert response.status_code == 200
    assert options is not None
    assert 'value="CNHKG"' not in options.group(1)
    assert 'value="AUMEL"' not in options.group(1)
    assert 'value="USCHI"' in options.group(1)
    assert locations == original_locations
