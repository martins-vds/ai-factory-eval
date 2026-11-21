import re

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.booking.interfaces.dialogs.views import create_booking_dialog_views
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository

cargo_repository = DjangoCargoRepository()
location_repository = DjangoLocationRepository()
locations = []
dashboard_view, _ = create_booking_views(CargoDashboard(cargo_repository))
destination_dialog_view, deadline_dialog_view = create_booking_dialog_views(
    CargoDashboard(cargo_repository),
    CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
    lambda: locations,
)

urlpatterns = [
    path('admin/dashboard/', dashboard_view),
    path('admin/cargo/<str:tracking_id>/destination/', destination_dialog_view),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_dialog_view),
]


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_shows_initial_values_and_stable_filtered_options(client):
    call_command('seed_sample_data')
    locations[:] = location_repository.find_all()
    initial_locations = locations.copy()

    first_response = client.get('/admin/cargo/DEF789/destination/')
    second_response = client.get('/admin/cargo/DEF789/destination/')
    content = first_response.content.decode()
    options = re.search(r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', content, re.DOTALL)

    assert first_response.status_code == second_response.status_code == 200
    assert 'Hong Kong' in content
    assert 'Melbourne' in content
    assert options is not None
    assert 'value="CNHKG"' not in options.group(1)
    assert 'value="AUMEL"' not in options.group(1)
    assert 'value="USNYC"' in options.group(1)
    assert len(re.findall(r'<option\b', options.group(1))) == 11
    assert locations == initial_locations
    assert re.findall(
        r'<option\b[^>]*value="([^"]+)"', options.group(1)
    ) == re.findall(
        r'<option\b[^>]*value="([^"]+)"',
        re.search(
            r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>',
            second_response.content.decode(),
            re.DOTALL,
        ).group(1),
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_shows_cargo_route_fields_and_current_deadline(client):
    call_command('seed_sample_data')
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None

    response = client.get('/admin/cargo/DEF789/deadline/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Hong Kong' in content
    assert 'Melbourne' in content
    assert f'value="{cargo.route_specification.arrival_deadline.date().isoformat()}"' in content
