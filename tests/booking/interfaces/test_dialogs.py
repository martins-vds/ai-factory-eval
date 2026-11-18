import re
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from django.core.management import call_command
from django.test import RequestFactory, override_settings
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.booking.interfaces.dialogs.views import create_dialog_views
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository

cargo_repository = DjangoCargoRepository()
cargo_dashboard = CargoDashboard(cargo_repository)
specification = CargoSpecification(cargo_repository, DjangoHandlingEventRepository())
dashboard_view, cargo_details_view = create_booking_views(cargo_dashboard)
destination_view, deadline_view = create_dialog_views(
    specification,
    DjangoLocationRepository().find_all,
    cargo_dashboard,
)
urlpatterns = [
    path('admin/dashboard/', dashboard_view),
    path('admin/cargo/<str:tracking_id>/', cargo_details_view),
    path('admin/cargo/<str:tracking_id>/destination/', destination_view),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_view),
]


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_not_routed_table_opens_destination_and_deadline_dialogs(client):
    call_command('seed_sample_data')

    response = client.get('/admin/dashboard/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'href="/admin/cargo/DEF789/destination/"' in content
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in content
    assert 'href="/admin/cargo/DEF789/deadline/"' in content
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in content
    assert 'id="edit-dialog"' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_dialogs_return_not_found_for_unknown_cargo(client):
    response = client.get('/admin/cargo/MISSING1/destination/')

    assert response.status_code == 404


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_shows_current_values_and_excludes_origin_and_destination(client):
    call_command('seed_sample_data')

    response = client.get('/admin/cargo/DEF789/destination/')
    content = response.content.decode()
    options = re.search(r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', content, re.DOTALL)

    assert response.status_code == 200
    assert 'Hong Kong' in content
    assert 'Melbourne' in content
    assert options is not None
    assert 'value="CNHKG"' not in options.group(1)
    assert 'value="AUMEL"' not in options.group(1)
    assert 'Change destination' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_keeps_the_backing_location_list_stable():
    call_command('seed_sample_data')
    locations = DjangoLocationRepository().find_all()
    initial_locations = locations.copy()
    destination, _ = create_dialog_views(
        specification,
        lambda: locations,
        cargo_dashboard,
    )
    request = RequestFactory().get('/admin/cargo/DEF789/destination/')
    request.user = SimpleNamespace(is_authenticated=False)

    first = destination(request, 'DEF789').content
    second = destination(request, 'DEF789').content
    first_options = re.search(rb'<select\b[^>]*>(.*?)</select>', first, re.DOTALL)
    second_options = re.search(rb'<select\b[^>]*>(.*?)</select>', second, re.DOTALL)

    assert locations == initial_locations
    assert first_options is not None
    assert second_options is not None
    assert first_options.group(1) == second_options.group(1)


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_rejects_an_origin_as_a_destination(client):
    call_command('seed_sample_data')
    cargo_before = cargo_repository.find(TrackingId('DEF789'))
    assert cargo_before is not None

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'CNHKG'},
        HTTP_HX_REQUEST='true',
    )
    cargo_after = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 200
    assert 'Select a valid destination.' in response.content.decode()
    assert response['HX-Retarget'] == '#edit-dialog'
    assert response['HX-Reswap'] == 'innerHTML'
    assert cargo_after is not None
    assert cargo_after.route_specification == cargo_before.route_specification


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_updates_cargo_refreshes_rows_and_completes_without_warning(client):
    call_command('seed_sample_data')
    cargo_before = cargo_repository.find(TrackingId('DEF789'))
    assert cargo_before is not None

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'USNYC'},
        HTTP_HX_REQUEST='true',
    )
    cargo_after = cargo_repository.find(TrackingId('DEF789'))
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Not Routed Cargo' in content
    assert 'data-tracking-id="DEF789"' in content
    assert 'New York' in content
    assert f'{cargo_before.route_specification.arrival_deadline:%m/%d/%Y}' in content
    assert 'Widget for var' not in content
    assert '<div id="edit-dialog" aria-live="polite"></div>' in content
    assert cargo_after is not None
    assert cargo_after.route_specification.origin == cargo_before.route_specification.origin
    assert cargo_after.route_specification.destination.unlocode.value == 'USNYC'
    assert (
        cargo_after.route_specification.arrival_deadline
        == cargo_before.route_specification.arrival_deadline
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_shows_initial_specification_values(client):
    call_command('seed_sample_data')
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None

    response = client.get('/admin/cargo/DEF789/deadline/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Hong Kong' in content
    assert 'Melbourne' in content
    assert f'value="{cargo.route_specification.arrival_deadline:%Y-%m-%d}"' in content
    assert 'Change deadline' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_shows_a_field_error_for_unparseable_input(client):
    call_command('seed_sample_data')
    cargo_before = cargo_repository.find(TrackingId('DEF789'))
    assert cargo_before is not None

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': 'not-a-date'},
        HTTP_HX_REQUEST='true',
    )
    cargo_after = cargo_repository.find(TrackingId('DEF789'))
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Enter a valid arrival deadline.' in content
    assert 'id="deadline-error"' in content
    assert 'aria-describedby="deadline-error"' in content
    assert 'aria-invalid="true"' in content
    assert 'value="not-a-date"' in content
    assert response['HX-Retarget'] == '#edit-dialog'
    assert response['HX-Reswap'] == 'innerHTML'
    assert cargo_after is not None
    assert cargo_after.route_specification == cargo_before.route_specification


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_updates_cargo_refreshes_rows_and_completes_without_warning(client):
    call_command('seed_sample_data')
    cargo_before = cargo_repository.find(TrackingId('DEF789'))
    assert cargo_before is not None

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': '2027-01-15'},
        HTTP_HX_REQUEST='true',
    )
    cargo_after = cargo_repository.find(TrackingId('DEF789'))
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Not Routed Cargo' in content
    assert 'data-tracking-id="DEF789"' in content
    assert '01/15/2027' in content
    assert 'Widget for var' not in content
    assert '<div id="edit-dialog" aria-live="polite"></div>' in content
    assert cargo_after is not None
    assert cargo_after.route_specification.origin == cargo_before.route_specification.origin
    assert (
        cargo_after.route_specification.destination == cargo_before.route_specification.destination
    )
    assert cargo_after.route_specification.arrival_deadline == datetime(2027, 1, 15, tzinfo=UTC)
