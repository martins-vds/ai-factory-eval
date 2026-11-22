import re
from datetime import date

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

location_list = []
cargo_repository = DjangoCargoRepository()
location_repository = DjangoLocationRepository()
dashboard = CargoDashboard(cargo_repository)
specification = CargoSpecification(cargo_repository, DjangoHandlingEventRepository())
dashboard_view, _ = create_booking_views(dashboard)
destination_dialog_view, deadline_dialog_view = create_booking_dialog_views(
    specification,
    dashboard,
    lambda: location_list,
)

urlpatterns = [
    path('admin/dashboard/', dashboard_view),
    path('admin/cargo/<str:tracking_id>/destination/', destination_dialog_view),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_dialog_view),
]


@pytest.fixture(autouse=True)
def seed_dialog_data():
    call_command('seed_sample_data')
    location_list[:] = location_repository.find_all()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_not_routed_table_opens_edit_dialogs_without_changing_table_behavior(client):
    response = client.get('/admin/dashboard/')
    content = response.content.decode()
    not_routed_table = content.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]

    assert response.status_code == 200
    assert 'data-tracking-id="DEF789"' in not_routed_table
    assert 'href="/admin/cargo/DEF789/route/"' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in not_routed_table
    assert 'hx-target="#cargo-edit-dialog"' in not_routed_table
    assert 'id="cargo-edit-dialog"' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_filters_options_without_mutating_locations(client):
    original_locations = location_list.copy()

    first_response = client.get('/admin/cargo/DEF789/destination/')
    second_response = client.get('/admin/cargo/DEF789/destination/')
    first_content = first_response.content.decode()
    second_content = second_response.content.decode()
    options = re.search(
        r'<select\b[^>]*id="destination"[^>]*>(.*?)</select>', first_content, re.DOTALL
    )
    first_option_values = re.findall(r'<option\b[^>]*value="([^"]+)"', first_content)
    second_option_values = re.findall(r'<option\b[^>]*value="([^"]+)"', second_content)

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert 'Origin: Hong Kong (CNHKG)' in first_content
    assert 'Current destination: Melbourne (AUMEL)' in first_content
    assert options is not None
    assert 'value="CNHKG"' not in options.group(1)
    assert 'value="AUMEL"' not in options.group(1)
    assert first_option_values == second_option_values
    assert location_list == original_locations


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_shows_current_value_and_parse_error(client):
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None

    response = client.get('/admin/cargo/DEF789/deadline/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Origin: Hong Kong (CNHKG)' in content
    assert 'Destination: Melbourne (AUMEL)' in content
    assert f'value="{cargo.route_specification.arrival_deadline.date().isoformat()}"' in content

    invalid_response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': 'not-a-date'},
        HTTP_HX_REQUEST='true',
    )

    assert invalid_response.status_code == 400
    assert 'Enter a valid arrival deadline.' in invalid_response.content.decode()
    assert 'aria-invalid="true"' in invalid_response.content.decode()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_update_preserves_other_fields_and_refreshes_table(client):
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    original_origin = cargo.route_specification.origin
    original_deadline = cargo.route_specification.arrival_deadline

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'USCHI'},
        HTTP_HX_REQUEST='true',
    )
    updated_cargo = cargo_repository.find(TrackingId('DEF789'))
    dashboard_response = client.get('/admin/dashboard/')

    assert response.status_code == 204
    assert response.headers['HX-Redirect'] == '/admin/dashboard/'
    assert updated_cargo is not None
    assert updated_cargo.route_specification.origin == original_origin
    assert updated_cargo.route_specification.arrival_deadline == original_deadline
    assert updated_cargo.route_specification.destination.unlocode.value == 'USCHI'
    dashboard_content = dashboard_response.content.decode()
    assert 'Chicago' in dashboard_content
    assert 'USCHI' in dashboard_content
    assert 'Melbourne' not in dashboard_content
    assert response.content == b''


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_update_preserves_other_fields_and_refreshes_table(client):
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    original_origin = cargo.route_specification.origin
    original_destination = cargo.route_specification.destination

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': '2026-12-01'},
        HTTP_HX_REQUEST='true',
    )
    updated_cargo = cargo_repository.find(TrackingId('DEF789'))
    dashboard_response = client.get('/admin/dashboard/')

    assert response.status_code == 204
    assert response.headers['HX-Redirect'] == '/admin/dashboard/'
    assert updated_cargo is not None
    assert updated_cargo.route_specification.origin == original_origin
    assert updated_cargo.route_specification.destination == original_destination
    assert updated_cargo.route_specification.arrival_deadline.date() == date(2026, 12, 1)
    assert '12/01/2026' in dashboard_response.content.decode()
    assert response.content == b''


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_missing_cargo_renders_an_error_fragment(client):
    response = client.get('/admin/cargo/MISSING1/destination/')

    assert response.status_code == 404
    assert 'Cargo MISSING1 not found.' in response.content.decode()
