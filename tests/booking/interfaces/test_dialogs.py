import re

import pytest
from django.core.management import call_command
from django.test import RequestFactory, override_settings
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
cargo_dashboard = CargoDashboard(cargo_repository)
specification = CargoSpecification(cargo_repository, DjangoHandlingEventRepository())
dashboard_view, _ = create_booking_views(cargo_dashboard)
destination_dialog_view, deadline_dialog_view = create_booking_dialog_views(
    cargo_dashboard,
    specification,
    location_repository.find_all,
)
urlpatterns = [
    path('admin/dashboard/', dashboard_view),
    path('admin/cargo/<str:tracking_id>/destination/', destination_dialog_view),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_dialog_view),
]


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_not_routed_table_opens_destination_and_deadline_dialogs(client):
    call_command('seed_sample_data')

    response = client.get('/admin/dashboard/')
    content = response.content.decode()
    not_routed_table = content.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]

    assert response.status_code == 200
    assert 'href="/admin/cargo/DEF789/route/"' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in not_routed_table
    assert 'id="booking-dialog-container"' in content
    assert 'hx-on::response-error=' in content


@pytest.mark.django_db
def test_destination_options_are_stable_and_do_not_mutate_available_locations():
    call_command('seed_sample_data')
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    locations = location_repository.find_all()
    original_locations = list(locations)
    view, _ = create_booking_dialog_views(
        cargo_dashboard,
        specification,
        lambda: locations,
    )
    request = RequestFactory().get('/admin/cargo/DEF789/destination/')

    first_response = view(request, 'DEF789')
    second_response = view(request, 'DEF789')
    first_options = re.findall(r'<option value="([^"]+)"', first_response.content.decode())
    second_options = re.findall(r'<option value="([^"]+)"', second_response.content.decode())
    first_content = first_response.content.decode()

    assert first_response.status_code == 200
    assert cargo.route_specification.origin.unlocode.value not in first_options
    assert cargo.route_specification.destination.unlocode.value not in first_options
    assert first_options == second_options
    assert locations == original_locations
    assert cargo.route_specification.origin.name in first_content
    assert cargo.route_specification.destination.name in first_content
    assert 'method="dialog"' in first_content
    assert 'Cancel' in first_content


@pytest.mark.parametrize('destination', ['CNHKG', 'UNKNOWN'])
@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_rejects_unavailable_destinations(client, destination):
    call_command('seed_sample_data')
    original = cargo_repository.find(TrackingId('DEF789'))
    assert original is not None

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': destination},
        HTTP_HX_REQUEST='true',
    )
    updated = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 200
    assert 'Select a valid destination.' in response.content.decode()
    assert 'aria-invalid="true"' in response.content.decode()
    assert updated is not None
    assert updated.route_specification.destination == original.route_specification.destination


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_shows_initial_value_and_parse_error(client):
    call_command('seed_sample_data')
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None

    initial_response = client.get('/admin/cargo/DEF789/deadline/')
    initial_content = initial_response.content.decode()
    invalid_response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': 'not-a-date'},
        HTTP_HX_REQUEST='true',
    )
    invalid_content = invalid_response.content.decode()

    assert f'value="{cargo.route_specification.arrival_deadline:%Y-%m-%d}"' in initial_content
    assert invalid_response.status_code == 200
    assert 'Enter a valid arrival deadline.' in invalid_content
    assert 'aria-invalid="true"' in invalid_content
    assert cargo_repository.find(TrackingId('DEF789')).route_specification.arrival_deadline == (
        cargo.route_specification.arrival_deadline
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_updates_cargo_and_refreshes_not_routed_table(client):
    call_command('seed_sample_data')
    original = cargo_repository.find(TrackingId('DEF789'))
    assert original is not None

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'USNYC'},
        HTTP_HX_REQUEST='true',
    )
    updated = cargo_repository.find(TrackingId('DEF789'))
    dashboard = client.get('/admin/dashboard/').content.decode()
    not_routed_table = dashboard.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]

    assert response.status_code == 204
    assert response.headers['HX-Redirect'] == '/admin/dashboard/'
    assert 'Widget for var' not in response.content.decode()
    assert updated is not None
    assert updated.route_specification.origin == original.route_specification.origin
    assert updated.route_specification.destination.unlocode.value == 'USNYC'
    assert (
        updated.route_specification.arrival_deadline
        == original.route_specification.arrival_deadline
    )
    assert 'New York' in not_routed_table
    assert 'USNYC' in not_routed_table
    assert 'AUMEL' not in not_routed_table


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_updates_cargo_and_refreshes_not_routed_table(client):
    call_command('seed_sample_data')
    original = cargo_repository.find(TrackingId('DEF789'))
    assert original is not None

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': '2035-02-01'},
        HTTP_HX_REQUEST='true',
    )
    updated = cargo_repository.find(TrackingId('DEF789'))
    dashboard = client.get('/admin/dashboard/').content.decode()
    not_routed_table = dashboard.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]

    assert response.status_code == 204
    assert response.headers['HX-Redirect'] == '/admin/dashboard/'
    assert updated is not None
    assert updated.route_specification.origin == original.route_specification.origin
    assert updated.route_specification.destination == original.route_specification.destination
    assert updated.route_specification.arrival_deadline.strftime('%Y-%m-%d') == '2035-02-01'
    assert '02/01/2035' in not_routed_table
