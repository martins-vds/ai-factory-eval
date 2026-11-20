import re

import pytest
from django.core.management import call_command
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.booking.interfaces.dialogs.views import create_dialog_views
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository

pytestmark = pytest.mark.django_db

cargo_repository = DjangoCargoRepository()
location_repository = DjangoLocationRepository()
shipping_locations = []
dashboard = CargoDashboard(cargo_repository)
dashboard_view, _ = create_booking_views(CargoDashboard(cargo_repository))
specification = CargoSpecification(cargo_repository, DjangoHandlingEventRepository())


def _shipping_locations():
    return shipping_locations


destination_dialog_view, deadline_dialog_view = create_dialog_views(
    dashboard,
    specification,
    _shipping_locations,
)

urlpatterns = [
    path('admin/dashboard/', dashboard_view),
    path('admin/cargo/<str:tracking_id>/destination/', destination_dialog_view),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_dialog_view),
]


@pytest.fixture(autouse=True)
def seed_data(settings):
    settings.ROOT_URLCONF = __name__
    call_command('seed_sample_data')
    shipping_locations[:] = location_repository.find_all()


def test_not_routed_table_opens_destination_and_deadline_dialogs(client):
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None

    response = client.get('/admin/dashboard/')
    not_routed_table = (
        response.content.decode().split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]
    )

    assert response.status_code == 200
    assert f'hx-get="/admin/cargo/{cargo.tracking_id.value}/destination/"' in not_routed_table
    assert f'hx-get="/admin/cargo/{cargo.tracking_id.value}/deadline/"' in not_routed_table
    assert f'href="/admin/cargo/{cargo.tracking_id.value}/route/"' in not_routed_table
    assert 'id="cargo-edit-dialog"' in not_routed_table


def test_destination_dialog_shows_current_values_and_filters_options_stably(client):
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    original_locations = tuple(shipping_locations)

    first_response = client.get('/admin/cargo/DEF789/destination/', HTTP_HX_REQUEST='true')
    second_response = client.get('/admin/cargo/DEF789/destination/', HTTP_HX_REQUEST='true')
    first_content = first_response.content.decode()
    second_content = second_response.content.decode()
    first_options = re.findall(r'<option value="([^"]+)"', first_content)
    second_options = re.findall(r'<option value="([^"]+)"', second_content)
    excluded_codes = {
        cargo.route_specification.origin.unlocode.value,
        cargo.route_specification.destination.unlocode.value,
    }

    assert first_response.status_code == second_response.status_code == 200
    assert cargo.route_specification.origin.name in first_content
    assert cargo.route_specification.destination.name in first_content
    assert len(first_options) == len(original_locations) - 2
    assert not excluded_codes.intersection(first_options)
    assert first_options == second_options
    assert tuple(shipping_locations) == original_locations


def test_invalid_destination_keeps_the_dialog_open_without_updating_cargo(client):
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': cargo.route_specification.origin.unlocode.value},
        HTTP_HX_REQUEST='true',
    )
    updated_cargo = cargo_repository.find(cargo.tracking_id)

    assert response.status_code == 200
    assert 'Select a valid destination.' in response.content.decode()
    assert 'aria-invalid="true"' in response.content.decode()
    assert updated_cargo is not None
    assert updated_cargo.route_specification.destination == cargo.route_specification.destination


def test_destination_update_redirects_and_refreshes_the_not_routed_row(client):
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    new_destination = next(
        location
        for location in shipping_locations
        if location
        not in (cargo.route_specification.origin, cargo.route_specification.destination)
    )

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': new_destination.unlocode.value},
        HTTP_HX_REQUEST='true',
    )
    updated_cargo = cargo_repository.find(cargo.tracking_id)
    dashboard_response = client.get('/admin/dashboard/')
    not_routed_table = (
        dashboard_response.content.decode()
        .split('id="not-routed-cargo"', 1)[1]
        .split('</section>', 1)[0]
    )

    assert response.status_code == 204
    assert response['HX-Redirect'] == '/admin/dashboard/'
    assert updated_cargo is not None
    assert updated_cargo.route_specification.origin == cargo.route_specification.origin
    assert updated_cargo.route_specification.destination == new_destination
    assert (
        updated_cargo.route_specification.arrival_deadline
        == cargo.route_specification.arrival_deadline
    )
    assert new_destination.name in not_routed_table


def test_deadline_dialog_shows_current_route_and_deadline(client):
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None

    response = client.get('/admin/cargo/DEF789/deadline/', HTTP_HX_REQUEST='true')
    content = response.content.decode()

    assert response.status_code == 200
    assert cargo.route_specification.origin.name in content
    assert cargo.route_specification.destination.name in content
    assert f'value="{cargo.route_specification.arrival_deadline.date().isoformat()}"' in content


@pytest.mark.parametrize('deadline', ['not-a-date', ''])
def test_invalid_deadline_shows_field_error_without_updating_cargo(client, deadline):
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': deadline},
        HTTP_HX_REQUEST='true',
    )
    updated_cargo = cargo_repository.find(cargo.tracking_id)

    assert response.status_code == 200
    assert 'Enter a valid arrival deadline.' in response.content.decode()
    assert 'aria-invalid="true"' in response.content.decode()
    assert updated_cargo is not None
    assert (
        updated_cargo.route_specification.arrival_deadline
        == cargo.route_specification.arrival_deadline
    )


def test_deadline_update_preserves_route_and_refreshes_the_not_routed_row(client):
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    new_deadline = '2031-02-03'

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': new_deadline},
        HTTP_HX_REQUEST='true',
    )
    updated_cargo = cargo_repository.find(cargo.tracking_id)
    dashboard_response = client.get('/admin/dashboard/')
    not_routed_table = (
        dashboard_response.content.decode()
        .split('id="not-routed-cargo"', 1)[1]
        .split('</section>', 1)[0]
    )

    assert response.status_code == 204
    assert response['HX-Redirect'] == '/admin/dashboard/'
    assert updated_cargo is not None
    assert updated_cargo.route_specification.origin == cargo.route_specification.origin
    assert updated_cargo.route_specification.destination == cargo.route_specification.destination
    assert updated_cargo.route_specification.arrival_deadline.date().isoformat() == new_deadline
    assert '02/03/2031' in not_routed_table


@pytest.mark.parametrize('dialog', ['destination', 'deadline'])
def test_missing_cargo_renders_an_error_for_the_dialog(client, dialog):
    response = client.get(f'/admin/cargo/MISSING1/{dialog}/', HTTP_HX_REQUEST='true')

    assert response.status_code == 404
    assert 'Cargo MISSING1 was not found.' in response.content.decode()
