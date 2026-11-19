import re

import pytest
from django.core.management import call_command
from django.test import RequestFactory

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.booking.interfaces.dialogs.views import create_destination_dialog_view
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository


@pytest.mark.django_db
def test_destination_dialog_shows_current_route_and_excludes_origin_and_destination():
    call_command('seed_sample_data')
    cargo_repository = DjangoCargoRepository()
    destination_view = create_destination_dialog_view(
        CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
        CargoDashboard(cargo_repository),
        DjangoLocationRepository().find_all,
    )

    response = destination_view(
        RequestFactory().get('/admin/cargo/DEF789/destination/'), 'DEF789'
    )
    content = response.content.decode()
    options = re.search(r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', content, re.DOTALL)

    assert response.status_code == 200
    assert 'Hong Kong' in content and 'Melbourne' in content
    assert options is not None
    assert 'value="CNHKG"' not in options.group(1)
    assert 'value="AUMEL"' not in options.group(1)
    assert 'Update' in content and 'Cancel' in content


@pytest.mark.django_db
def test_destination_dialog_updates_through_specification_and_refreshes_dashboard():
    call_command('seed_sample_data')
    cargo_repository = DjangoCargoRepository()
    tracking_id = TrackingId('DEF789')
    original = cargo_repository.find(tracking_id)
    assert original is not None
    destination_view = create_destination_dialog_view(
        CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
        CargoDashboard(cargo_repository),
        DjangoLocationRepository().find_all,
    )

    response = destination_view(
        RequestFactory().post(
            '/admin/cargo/DEF789/destination/',
            {'destination': 'USNYC'},
            HTTP_HX_REQUEST='true',
        ),
        'DEF789',
    )
    updated = cargo_repository.find(tracking_id)

    assert response.status_code == 200
    assert response['HX-Redirect'] == '/admin/dashboard/'
    assert updated is not None
    assert updated.route_specification.origin == original.route_specification.origin
    assert updated.route_specification.destination.unlocode.value == 'USNYC'
    assert updated.route_specification.arrival_deadline == original.route_specification.arrival_deadline
    assert updated.itinerary == original.itinerary
    assert 'Widget for var' not in response.content.decode()
