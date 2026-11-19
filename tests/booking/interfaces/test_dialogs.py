import re

import pytest
from django.core.management import call_command
from django.test import RequestFactory

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.booking.interfaces.dialogs.views import create_booking_dialog_views
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository


@pytest.mark.django_db
def test_destination_dialog_shows_current_values_and_keeps_filtered_options_stable():
    call_command('seed_sample_data')
    cargo_repository = DjangoCargoRepository()
    locations = DjangoLocationRepository().find_all()
    original_locations = locations.copy()
    destination_view, _ = create_booking_dialog_views(
        CargoDashboard(cargo_repository),
        CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
        lambda: locations,
    )
    request_factory = RequestFactory()

    responses = [
        destination_view(request_factory.get('/admin/cargo/DEF789/destination/'), 'DEF789')
        for _ in range(2)
    ]

    assert locations == original_locations
    for response in responses:
        content = response.content.decode()
        options = re.search(r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', content, re.DOTALL)
        assert response.status_code == 200
        assert 'Hong Kong' in content and 'CNHKG' in content
        assert 'Melbourne' in content and 'AUMEL' in content
        assert options is not None
        assert 'value="CNHKG"' not in options.group(1)
        assert 'value="AUMEL"' not in options.group(1)
        assert options.group(1).count('<option') == 12
