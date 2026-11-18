import re
from datetime import date

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
available_locations = []
dashboard = CargoDashboard(cargo_repository)
dashboard_view, cargo_details_view = create_booking_views(dashboard)
cargo_specification = CargoSpecification(cargo_repository, DjangoHandlingEventRepository())
deadline_dialog_view = create_deadline_dialog_view(
    dashboard,
    cargo_specification,
)
destination_dialog_view = create_destination_dialog_view(
    dashboard,
    cargo_specification,
    lambda: available_locations,
)
urlpatterns = [
    path('admin/dashboard/', dashboard_view),
    path('admin/cargo/<str:tracking_id>/', cargo_details_view),
    path('admin/cargo/<str:tracking_id>/destination/', destination_dialog_view),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_dialog_view),
]


@pytest.fixture(autouse=True)
def reset_available_locations():
    available_locations.clear()
    yield
    available_locations.clear()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_not_routed_rows_open_destination_and_deadline_dialogs(client):
    call_command('seed_sample_data')

    response = client.get('/admin/dashboard/')
    content = response.content.decode()
    not_routed_table = content.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]

    assert response.status_code == 200
    assert 'href="/admin/cargo/DEF789/route/"' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in not_routed_table
    assert 'hx-target="#booking-dialog"' in not_routed_table
    assert 'id="booking-dialog"' in content
    assert 'hx-on::before-swap=' in content
    assert 'hx-on::after-settle=' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_shows_the_current_deadline_and_route_context(client):
    call_command('seed_sample_data')
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None

    response = client.get(
        '/admin/cargo/DEF789/deadline/',
        HTTP_HX_REQUEST='true',
    )
    content = response.content.decode()

    assert response.status_code == 200
    assert f'value="{cargo.route_specification.arrival_deadline.date().isoformat()}"' in content
    assert cargo.route_specification.origin.name in content
    assert cargo.route_specification.destination.name in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
@pytest.mark.parametrize('value', ('not-a-date', '2027-W05-1'))
def test_deadline_dialog_reports_an_invalid_date_without_changing_cargo(client, value):
    call_command('seed_sample_data')
    cargo_before = cargo_repository.find(TrackingId('DEF789'))
    assert cargo_before is not None

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': value},
        HTTP_HX_REQUEST='true',
    )
    cargo_after = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 200
    assert b'Enter a valid arrival deadline.' in response.content
    assert b'aria-invalid="true"' in response.content
    assert cargo_after == cargo_before


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_updates_deadline_and_preserves_other_route_fields(client):
    call_command('seed_sample_data')
    cargo_before = cargo_repository.find(TrackingId('DEF789'))
    assert cargo_before is not None
    new_deadline = date(2027, 2, 1)

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': new_deadline.isoformat()},
        HTTP_HX_REQUEST='true',
    )
    cargo_after = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 204
    assert response.content == b''
    assert response.headers['HX-Redirect'] == '/admin/dashboard/'
    assert cargo_after is not None
    assert cargo_after.route_specification.arrival_deadline.date() == new_deadline
    assert cargo_after.route_specification.origin == cargo_before.route_specification.origin
    assert (
        cargo_after.route_specification.destination == cargo_before.route_specification.destination
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_refreshes_dashboard_rows_after_update(client):
    call_command('seed_sample_data')

    client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': date(2027, 2, 1).isoformat()},
        HTTP_HX_REQUEST='true',
    )
    response = client.get('/admin/dashboard/')
    not_routed_table = response.content.decode().split('id="not-routed-cargo"', 1)[1]

    assert response.status_code == 200
    assert '02/01/2027' in not_routed_table


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_filters_options_without_mutating_them(client):
    call_command('seed_sample_data')
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    available_locations[:] = location_repository.find_all()
    initial_locations = available_locations.copy()

    response = client.get(
        '/admin/cargo/DEF789/destination/',
        HTTP_HX_REQUEST='true',
    )
    content = response.content.decode()
    options = re.findall(r'<option value="([^"]+)"', content)
    repeat_response = client.get(
        '/admin/cargo/DEF789/destination/',
        HTTP_HX_REQUEST='true',
    )
    repeat_options = re.findall(r'<option value="([^"]+)"', repeat_response.content.decode())

    assert response.status_code == 200
    assert cargo.route_specification.origin.unlocode.value not in options
    assert cargo.route_specification.destination.unlocode.value not in options
    assert cargo.route_specification.origin.name in content
    assert cargo.route_specification.destination.name in content
    assert available_locations == initial_locations
    assert repeat_options == options


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_updates_destination_and_preserves_other_route_fields(client):
    call_command('seed_sample_data')
    cargo_before = cargo_repository.find(TrackingId('DEF789'))
    assert cargo_before is not None
    available_locations[:] = location_repository.find_all()
    destination = next(
        location
        for location in available_locations
        if location
        not in (
            cargo_before.route_specification.origin,
            cargo_before.route_specification.destination,
        )
    )

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': destination.unlocode.value},
        HTTP_HX_REQUEST='true',
    )
    cargo_after = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 204
    assert response.content == b''
    assert response.headers['HX-Redirect'] == '/admin/dashboard/'
    assert cargo_after is not None
    assert cargo_after.route_specification.destination == destination
    assert cargo_after.route_specification.origin == cargo_before.route_specification.origin
    assert (
        cargo_after.route_specification.arrival_deadline
        == cargo_before.route_specification.arrival_deadline
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_refuses_origin_as_new_destination(client):
    call_command('seed_sample_data')
    cargo_before = cargo_repository.find(TrackingId('DEF789'))
    assert cargo_before is not None
    available_locations[:] = location_repository.find_all()

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': cargo_before.route_specification.origin.unlocode.value},
        HTTP_HX_REQUEST='true',
    )
    cargo_after = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 200
    assert b'Choose a valid destination.' in response.content
    assert b'aria-invalid="true"' in response.content
    assert cargo_after == cargo_before


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
@pytest.mark.parametrize(
    'url',
    (
        '/admin/cargo/MISSING1/destination/',
        '/admin/cargo/MISSING1/deadline/',
    ),
)
def test_dialogs_return_not_found_for_unknown_cargo(client, url):
    call_command('seed_sample_data')

    response = client.get(url, HTTP_HX_REQUEST='true')

    assert response.status_code == 404
    assert b'Cargo with tracking ID MISSING1 not found.' in response.content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_full_page_dialog_returns_not_found_for_unknown_cargo(client):
    call_command('seed_sample_data')

    response = client.get('/admin/cargo/MISSING1/deadline/')

    assert response.status_code == 404


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_supports_full_page_fallback(client):
    call_command('seed_sample_data')

    response = client.get('/admin/cargo/DEF789/deadline/')

    assert response.status_code == 200
    assert b'<html lang="en">' in response.content
    assert b'<dialog open' in response.content
