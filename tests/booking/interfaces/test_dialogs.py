import re
from datetime import UTC, datetime

import pytest
from django.core.management import call_command
from django.template.loader import render_to_string
from django.test import RequestFactory, override_settings
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.booking.interfaces.dialogs.views import create_booking_dialog_views
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository

cargo_repository = DjangoCargoRepository()
location_repository = DjangoLocationRepository()
destination_dialog_view, deadline_dialog_view = create_booking_dialog_views(
    CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
    CargoDashboard(cargo_repository),
    location_repository.find_all,
)
urlpatterns = [
    path('admin/cargo/<str:tracking_id>/destination/', destination_dialog_view),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_dialog_view),
]


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_shows_current_values_and_excludes_origin_and_destination(client):
    call_command('seed_sample_data')
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None

    response = client.get('/admin/cargo/DEF789/destination/')
    content = response.content.decode()
    options = re.search(r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', content, re.DOTALL)

    assert response.status_code == 200
    assert 'Change destination' in content
    assert cargo.route_specification.origin.name in content
    assert cargo.route_specification.destination.name in content
    assert options is not None
    assert cargo.route_specification.origin.unlocode.value not in options.group(1)
    assert cargo.route_specification.destination.unlocode.value not in options.group(1)


@pytest.mark.django_db
def test_destination_options_do_not_mutate_locations_across_renders():
    call_command('seed_sample_data')
    locations = location_repository.find_all()
    original_locations = locations.copy()
    destination_view, _ = create_booking_dialog_views(
        CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
        CargoDashboard(cargo_repository),
        lambda: locations,
    )
    request = RequestFactory().get('/admin/cargo/DEF789/destination/')

    first_response = destination_view(request, 'DEF789')
    second_response = destination_view(request, 'DEF789')
    first_options = re.search(
        r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>',
        first_response.content.decode(),
        re.DOTALL,
    )
    second_options = re.search(
        r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>',
        second_response.content.decode(),
        re.DOTALL,
    )

    assert locations == original_locations
    assert first_options is not None and second_options is not None
    assert first_options.group(1) == second_options.group(1)


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_update_uses_specification_and_redirects_after_completion(client):
    call_command('seed_sample_data')
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    destination = next(
        location
        for location in location_repository.find_all()
        if location not in (cargo.route_specification.origin, cargo.route_specification.destination)
    )

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': destination.unlocode.value},
        headers={'HX-Request': 'true'},
    )
    updated_cargo = cargo_repository.find(cargo.tracking_id)

    assert response.status_code == 204
    assert response.headers['HX-Redirect'] == '/admin/dashboard/'
    assert updated_cargo is not None
    assert updated_cargo.route_specification.origin == cargo.route_specification.origin
    assert updated_cargo.route_specification.destination == destination
    assert updated_cargo.route_specification.arrival_deadline == (
        cargo.route_specification.arrival_deadline
    )
    assert updated_cargo.itinerary == cargo.itinerary


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_invalid_destination_keeps_the_dialog_open_with_a_field_error(client):
    call_command('seed_sample_data')
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': cargo.route_specification.origin.unlocode.value},
    )
    updated_cargo = cargo_repository.find(cargo.tracking_id)
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Select a valid destination.' in content
    assert 'aria-invalid="true"' in content
    assert updated_cargo is not None
    assert updated_cargo.route_specification.destination == (
        cargo.route_specification.destination
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_invalid_deadline_shows_a_field_error_without_changing_cargo(client):
    call_command('seed_sample_data')
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': 'not-a-date'},
    )
    updated_cargo = cargo_repository.find(cargo.tracking_id)

    assert response.status_code == 200
    assert 'Enter a valid arrival deadline.' in response.content.decode()
    assert 'aria-invalid="true"' in response.content.decode()
    assert updated_cargo is not None
    assert updated_cargo.route_specification.arrival_deadline == (
        cargo.route_specification.arrival_deadline
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_dialog_views_return_not_found_and_reject_other_methods(client):
    call_command('seed_sample_data')

    assert client.get('/admin/cargo/MISSING1/destination/').status_code == 404
    assert client.get('/admin/cargo/MISSING1/deadline/').status_code == 404
    assert client.put('/admin/cargo/DEF789/destination/').status_code == 405
    assert client.put('/admin/cargo/DEF789/deadline/').status_code == 405


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_update_preserves_route_fields_and_refreshes_the_dashboard(client):
    call_command('seed_sample_data')
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    expected_deadline = datetime(2031, 2, 3, tzinfo=UTC)

    initial_response = client.get('/admin/cargo/DEF789/deadline/')
    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': '2031-02-03'},
        headers={'HX-Request': 'true'},
    )
    updated_cargo = cargo_repository.find(cargo.tracking_id)

    assert initial_response.status_code == 200
    assert f'value="{cargo.route_specification.arrival_deadline.date().isoformat()}"' in (
        initial_response.content.decode()
    )
    assert cargo.route_specification.origin.name in initial_response.content.decode()
    assert cargo.route_specification.destination.name in initial_response.content.decode()
    assert response.status_code == 204
    assert response.headers['HX-Redirect'] == '/admin/dashboard/'
    assert updated_cargo is not None
    assert updated_cargo.route_specification.origin == cargo.route_specification.origin
    assert updated_cargo.route_specification.destination == cargo.route_specification.destination
    assert updated_cargo.route_specification.arrival_deadline == expected_deadline
    assert updated_cargo.itinerary == cargo.itinerary


@pytest.mark.django_db
def test_not_routed_table_opens_destination_and_deadline_dialogs():
    call_command('seed_sample_data')
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None

    content = render_to_string(
        'booking/dashboard/not_routed_table.html',
        {'not_routed_cargos': [cargo]},
    )

    assert 'href="/admin/cargo/DEF789/route/"' in content
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in content
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in content
    assert 'id="cargo-edit-dialog"' in content
