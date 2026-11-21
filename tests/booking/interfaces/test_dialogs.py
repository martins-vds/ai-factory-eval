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


@pytest.fixture(autouse=True)
def reset_locations():
    locations.clear()


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
    assert re.findall(r'<option\b[^>]*value="([^"]+)"', options.group(1)) == re.findall(
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


@pytest.mark.parametrize('dialog', ('destination', 'deadline'))
@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_unknown_cargo_dialog_returns_not_found(client, dialog):
    call_command('seed_sample_data')

    response = client.get(f'/admin/cargo/MISSING1/{dialog}/')

    assert response.status_code == 404


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_unparseable_deadline_is_reported_at_the_deadline_field(client):
    call_command('seed_sample_data')
    tracking_id = TrackingId('DEF789')
    original = cargo_repository.find(tracking_id)
    assert original is not None

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': 'not-a-date'},
        HTTP_HX_REQUEST='true',
    )
    content = response.content.decode()
    updated = cargo_repository.find(tracking_id)

    assert response.status_code == 200
    assert 'Enter a valid arrival deadline.' in content
    assert 'id="deadline-error"' in content
    assert 'aria-invalid="true"' in content
    assert 'aria-describedby="deadline-error"' in content
    assert updated is not None
    assert (
        updated.route_specification.arrival_deadline
        == original.route_specification.arrival_deadline
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_update_rejects_origin_as_a_new_destination(client):
    call_command('seed_sample_data')
    locations[:] = location_repository.find_all()
    tracking_id = TrackingId('DEF789')
    original = cargo_repository.find(tracking_id)
    assert original is not None

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'CNHKG'},
        HTTP_HX_REQUEST='true',
    )
    updated = cargo_repository.find(tracking_id)
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Select a valid destination.' in content
    assert 'aria-invalid="true"' in content
    assert updated is not None
    assert updated.route_specification == original.route_specification


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_update_completes_dialog_and_refreshes_the_not_routed_row(client):
    call_command('seed_sample_data')
    locations[:] = location_repository.find_all()
    tracking_id = TrackingId('DEF789')
    original = cargo_repository.find(tracking_id)
    assert original is not None

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'USNYC'},
        HTTP_HX_REQUEST='true',
    )
    updated = cargo_repository.find(tracking_id)
    dashboard = client.get('/admin/dashboard/').content.decode()
    not_routed_table = dashboard.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]

    assert response.status_code == 200
    assert response.content == b''
    assert 'bookingDialogCompleted' in response.headers['HX-Trigger']
    assert b'Widget' not in response.content
    assert updated is not None
    assert updated.route_specification.origin == original.route_specification.origin
    assert updated.route_specification.destination.name == 'New York'
    assert (
        updated.route_specification.arrival_deadline
        == original.route_specification.arrival_deadline
    )
    assert updated.itinerary == original.itinerary
    assert 'New York' in not_routed_table
    assert 'USNYC' in not_routed_table


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_update_completes_dialog_and_refreshes_the_not_routed_row(client):
    call_command('seed_sample_data')
    tracking_id = TrackingId('DEF789')
    original = cargo_repository.find(tracking_id)
    assert original is not None

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': '2027-01-15'},
        HTTP_HX_REQUEST='true',
    )
    updated = cargo_repository.find(tracking_id)
    dashboard = client.get('/admin/dashboard/').content.decode()
    not_routed_table = dashboard.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]

    assert response.status_code == 200
    assert response.content == b''
    assert 'bookingDialogCompleted' in response.headers['HX-Trigger']
    assert b'Widget' not in response.content
    assert updated is not None
    assert updated.route_specification.origin == original.route_specification.origin
    assert updated.route_specification.destination == original.route_specification.destination
    assert updated.route_specification.arrival_deadline.date().isoformat() == '2027-01-15'
    assert updated.itinerary == original.itinerary
    assert '01/15/2027' in not_routed_table


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_non_htmx_deadline_update_redirects_to_the_dashboard(client):
    call_command('seed_sample_data')

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': '2027-01-15'},
    )

    assert response.status_code == 302
    assert response.headers['Location'] == '/admin/dashboard/'
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    assert cargo.route_specification.arrival_deadline.date().isoformat() == '2027-01-15'


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_not_routed_table_opens_edit_dialogs_and_refreshes_after_completion(client):
    call_command('seed_sample_data')

    response = client.get('/admin/dashboard/')
    not_routed_table = (
        response.content.decode().split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]
    )

    assert response.status_code == 200
    assert 'href="/admin/cargo/DEF789/destination/"' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in not_routed_table
    assert 'Change destination' in not_routed_table
    assert 'href="/admin/cargo/DEF789/deadline/"' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in not_routed_table
    assert 'Change deadline' in not_routed_table
    assert 'hx-trigger="bookingDialogCompleted from:body"' in not_routed_table
    assert 'hx-select="#not-routed-cargo"' in not_routed_table
    assert 'hx-on::before-swap=' in not_routed_table
    assert 'hx-on::after-swap=' in not_routed_table
    assert 'showModal()' in not_routed_table
