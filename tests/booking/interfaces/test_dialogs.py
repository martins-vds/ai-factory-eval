from datetime import date
import re

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.booking.interfaces.dialogs.views import (
    create_deadline_dialog_view,
    create_destination_dialog_view,
)
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository

cargo_repository = DjangoCargoRepository()
location_repository = DjangoLocationRepository()
dashboard = CargoDashboard(cargo_repository)
destination_dialog_view = create_destination_dialog_view(
    dashboard,
    CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
    location_repository.find_all,
)
deadline_dialog_view = create_deadline_dialog_view(
    dashboard,
    CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
)
dashboard_view, _ = create_booking_views(dashboard)
urlpatterns = [
    path('admin/dashboard/', dashboard_view),
    path('admin/cargo/<str:tracking_id>/destination/', destination_dialog_view),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_dialog_view),
]


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_shows_current_route_specification_and_filtered_options(client):
    call_command('seed_sample_data')

    response = client.get('/admin/cargo/DEF789/destination/')
    content = response.content.decode()
    options = re.search(r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', content, re.DOTALL)

    assert response.status_code == 200
    assert 'Change destination' in content
    assert 'Hong Kong' in content
    assert 'Melbourne' in content
    assert options is not None
    assert 'CNHKG' not in options.group(1)
    assert 'AUMEL' not in options.group(1)


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_rejects_origin_without_changing_route(client):
    call_command('seed_sample_data')

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'CNHKG'},
        HTTP_HX_REQUEST='true',
    )
    cargo = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 200
    assert 'Select a valid destination.' in response.content.decode()
    assert 'aria-invalid="true"' in response.content.decode()
    assert cargo is not None
    assert cargo.route_specification.destination.unlocode.value == 'AUMEL'


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_shows_current_route_specification_and_deadline(client):
    call_command('seed_sample_data')
    cargo = dashboard.get_cargo_details(TrackingId('DEF789'))
    assert cargo is not None

    response = client.get('/admin/cargo/DEF789/deadline/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Change arrival deadline' in content
    assert 'Hong Kong' in content
    assert 'Melbourne' in content
    assert f'value="{cargo.route_specification.arrival_deadline.date().isoformat()}"' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_shows_parse_error_without_changing_deadline(client):
    call_command('seed_sample_data')
    cargo = dashboard.get_cargo_details(TrackingId('DEF789'))
    assert cargo is not None
    original_deadline = cargo.route_specification.arrival_deadline

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': 'not-a-date'},
        HTTP_HX_REQUEST='true',
    )
    content = response.content.decode()
    updated_cargo = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 200
    assert 'Enter a valid arrival deadline.' in content
    assert 'aria-invalid="true"' in content
    assert updated_cargo is not None
    assert updated_cargo.route_specification.arrival_deadline == original_deadline


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_updates_deadline_preserves_route_and_refreshes_table(client):
    call_command('seed_sample_data')
    cargo = dashboard.get_cargo_details(TrackingId('DEF789'))
    assert cargo is not None
    expected_deadline = date(2030, 11, 20)
    original_origin = cargo.route_specification.origin
    original_destination = cargo.route_specification.destination

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': expected_deadline.isoformat()},
        HTTP_HX_REQUEST='true',
    )
    updated_cargo = cargo_repository.find(TrackingId('DEF789'))
    refreshed_dashboard = client.get('/admin/dashboard/')
    not_routed_table = (
        refreshed_dashboard.content.decode()
        .split('id="not-routed-cargo"', 1)[1]
        .split('</section>', 1)[0]
    )

    assert response.status_code == 200
    assert response.content == b''
    assert response.headers['HX-Trigger'] == 'cargo-updated'
    assert b'Widget for var' not in response.content
    assert updated_cargo is not None
    assert updated_cargo.route_specification.arrival_deadline.date() == expected_deadline
    assert updated_cargo.route_specification.origin == original_origin
    assert updated_cargo.route_specification.destination == original_destination
    assert '11/20/2030' in not_routed_table
