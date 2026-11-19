import re
from datetime import date

import pytest
from django.core.management import call_command
from django.http import Http404
from django.test import RequestFactory
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
cargo_dashboard = CargoDashboard(cargo_repository)
cargo_specification = CargoSpecification(
    cargo_repository,
    DjangoHandlingEventRepository(),
)


def _shipping_locations():
    return shipping_locations


dashboard_view, _ = create_booking_views(cargo_dashboard)
destination_dialog_view, deadline_dialog_view = create_dialog_views(
    cargo_dashboard,
    cargo_specification,
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


def test_not_routed_table_exposes_dialog_controls_without_changing_route_link(client):
    response = client.get('/admin/dashboard/')
    not_routed_table = (
        response.content.decode().split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]
    )

    assert response.status_code == 200
    assert 'aria-haspopup="dialog"' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in not_routed_table
    assert 'id="cargo-edit-dialog"' in not_routed_table
    assert 'href="/admin/cargo/DEF789/route/"' in not_routed_table


def test_destination_dialog_filters_options_without_mutating_locations(client):
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    original_locations = tuple(shipping_locations)

    first_response = client.get('/admin/cargo/DEF789/destination/', HTTP_HX_REQUEST='true')
    second_response = client.get('/admin/cargo/DEF789/destination/', HTTP_HX_REQUEST='true')
    first_content = first_response.content.decode()
    second_content = second_response.content.decode()
    first_options = re.findall(r'<option\b[^>]*value="([^"]+)"', first_content)
    second_options = re.findall(r'<option\b[^>]*value="([^"]+)"', second_content)
    excluded_codes = {
        cargo.route_specification.origin.unlocode.value,
        cargo.route_specification.destination.unlocode.value,
    }

    assert first_response.status_code == second_response.status_code == 200
    assert cargo.route_specification.origin.name in first_content
    assert cargo.route_specification.destination.name in first_content
    assert len(first_options) == len(original_locations) - 2
    assert not excluded_codes.intersection(first_options)
    assert f'value="{first_options[0]}" selected' in first_content
    assert first_options == second_options
    assert tuple(shipping_locations) == original_locations


def test_deadline_dialog_shows_current_route_and_deadline(client):
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None

    response = client.get('/admin/cargo/DEF789/deadline/', HTTP_HX_REQUEST='true')
    content = response.content.decode()

    assert response.status_code == 200
    assert cargo.route_specification.origin.name in content
    assert cargo.route_specification.destination.name in content
    assert f'value="{cargo.route_specification.arrival_deadline.date().isoformat()}"' in content
    assert 'role="alert"' not in content


@pytest.mark.parametrize(
    'form_data',
    [{'deadline': 'not-a-date'}, {}, {'deadline': '20270115'}],
    ids=('malformed', 'missing', 'non-iso-format'),
)
def test_invalid_deadline_shows_field_error_and_keeps_dialog_open(client, form_data):
    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        form_data,
        HTTP_HX_REQUEST='true',
    )
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Enter a valid arrival deadline.' in content
    assert 'role="alert"' in content
    assert 'aria-invalid="true"' in content
    if not form_data:
        assert 'value=""' in content


def test_invalid_destination_shows_field_error_without_updating_cargo(client):
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': cargo.route_specification.origin.unlocode.value},
        HTTP_HX_REQUEST='true',
    )
    updated = cargo_repository.find(TrackingId('DEF789'))
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Select a valid destination.' in content
    assert 'role="alert"' in content
    assert 'aria-invalid="true"' in content
    assert updated is not None
    assert updated.route_specification.destination == cargo.route_specification.destination


def test_destination_update_redirects_and_refreshes_not_routed_row(client):
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    destinations = [
        location
        for location in shipping_locations
        if location not in (cargo.route_specification.origin, cargo.route_specification.destination)
    ]
    destination = destinations[1]

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': destination.unlocode.value},
        HTTP_HX_REQUEST='true',
    )
    updated = cargo_repository.find(TrackingId('DEF789'))
    dashboard = client.get('/admin/dashboard/').content.decode()
    not_routed_table = dashboard.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]

    assert response.status_code == 204
    assert response['HX-Redirect'] == '/admin/dashboard/'
    assert updated is not None
    assert updated.route_specification.origin == cargo.route_specification.origin
    assert updated.route_specification.destination == destination
    assert (
        updated.route_specification.arrival_deadline == cargo.route_specification.arrival_deadline
    )
    assert updated.itinerary == cargo.itinerary
    assert destination.name in not_routed_table
    assert 'Widget for var' not in response.content.decode()


def test_deadline_update_preserves_route_fields_and_refreshes_not_routed_row(client):
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    updated_date = date(2027, 1, 15)

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': updated_date.isoformat()},
    )
    updated = cargo_repository.find(TrackingId('DEF789'))
    dashboard = client.get('/admin/dashboard/').content.decode()
    not_routed_table = dashboard.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]

    assert response.status_code == 302
    assert response.url == '/admin/dashboard/'
    assert updated is not None
    assert updated.route_specification.origin == cargo.route_specification.origin
    assert updated.route_specification.destination == cargo.route_specification.destination
    assert updated.route_specification.arrival_deadline.date() == updated_date
    assert updated.itinerary == cargo.itinerary
    assert '01/15/2027' in not_routed_table
    assert 'Widget for var' not in response.content.decode()


def test_change_destination_use_case_rejects_the_cargo_origin():
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None

    with pytest.raises(ValueError, match="Origin and destination can't be the same"):
        cargo_specification.change_destination(cargo.tracking_id, cargo.route_specification.origin)


@pytest.mark.parametrize('dialog', ['destination', 'deadline'])
def test_unknown_dialog_cargo_returns_not_found(client, dialog):
    response = client.get(f'/admin/cargo/UNKNOWN/{dialog}/', HTTP_HX_REQUEST='true')
    view = destination_dialog_view if dialog == 'destination' else deadline_dialog_view

    assert response.status_code == 404
    with pytest.raises(
        Http404,
        match='^Cargo with tracking ID UNKNOWN not found\\.$',
    ):
        view(RequestFactory().get(f'/admin/cargo/UNKNOWN/{dialog}/'), 'UNKNOWN')
