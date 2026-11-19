import re
from datetime import UTC, datetime

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
from cargotracker.location.domain.un_locode import UnLocode
from cargotracker.location.infrastructure.repository import DjangoLocationRepository

TRACKING_ID = 'DEF789'
DASHBOARD_PATH = '/admin/dashboard/'
DESTINATION_PATH = f'/admin/cargo/{TRACKING_ID}/destination/'
DEADLINE_PATH = f'/admin/cargo/{TRACKING_ID}/deadline/'

cargo_repository = DjangoCargoRepository()
location_repository = DjangoLocationRepository()
available_locations = []
cargo_dashboard = CargoDashboard(cargo_repository)
cargo_specification = CargoSpecification(
    cargo_repository,
    DjangoHandlingEventRepository(),
)
destination_dialog, deadline_dialog = create_booking_dialog_views(
    cargo_specification,
    cargo_dashboard,
    lambda: available_locations,
)
dashboard, _ = create_booking_views(cargo_dashboard)
urlpatterns = [
    path('admin/dashboard/', dashboard),
    path('admin/cargo/<str:tracking_id>/destination/', destination_dialog),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_dialog),
]


@pytest.fixture
def seeded_booking_data():
    call_command('seed_sample_data')
    available_locations[:] = location_repository.find_all()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_shows_initial_route_and_stable_filtered_options(
    client, seeded_booking_data
):
    cargo = cargo_repository.find(TrackingId(TRACKING_ID))
    assert cargo is not None
    expected_locations = list(available_locations)

    first = client.get(DESTINATION_PATH)
    second = client.get(DESTINATION_PATH)
    content = first.content.decode()
    options = re.search(r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', content, re.DOTALL)
    subsequent_options = re.search(
        r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>',
        second.content.decode(),
        re.DOTALL,
    )
    assert options is not None and subsequent_options is not None

    origin = cargo.route_specification.origin
    current_destination = cargo.route_specification.destination
    assert first.status_code == second.status_code == 200
    assert f'Origin: {origin.name} ({origin.unlocode.value})' in content
    assert (
        f'Current destination: {current_destination.name} ({current_destination.unlocode.value})'
        in content
    )
    assert 'destination-error' not in content
    assert origin.unlocode.value not in options.group(1)
    assert current_destination.unlocode.value not in options.group(1)
    assert options.group(1).count('<option') == len(expected_locations) - 2
    assert options.group(1) == subsequent_options.group(1)
    assert available_locations == expected_locations


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_dialog_requests_render_partial_forms_with_their_post_actions(client, seeded_booking_data):
    destination_response = client.get(DESTINATION_PATH, HTTP_HX_REQUEST='true')
    deadline_response = client.get(DEADLINE_PATH, HTTP_HX_REQUEST='true')

    assert destination_response.status_code == deadline_response.status_code == 200
    assert '<!doctype html>' not in destination_response.content.decode().lower()
    assert '<!doctype html>' not in deadline_response.content.decode().lower()
    assert f'action="{DESTINATION_PATH}"' in destination_response.content.decode()
    assert f'action="{DEADLINE_PATH}"' in deadline_response.content.decode()
    assert 'Origin: Hong Kong (CNHKG)' in deadline_response.content.decode()
    assert 'Destination: Melbourne (AUMEL)' in deadline_response.content.decode()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_rejects_origin_as_a_submitted_destination(client, seeded_booking_data):
    cargo = cargo_repository.find(TrackingId(TRACKING_ID))
    assert cargo is not None

    response = client.post(
        DESTINATION_PATH,
        {'destination': cargo.route_specification.origin.unlocode.value},
        HTTP_HX_REQUEST='true',
    )
    updated_cargo = cargo_repository.find(cargo.tracking_id)

    assert response.status_code == 200
    assert 'Select a valid destination.' in response.content.decode()
    assert 'aria-invalid="true"' in response.content.decode()
    assert updated_cargo == cargo


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_rejects_a_missing_selection(client, seeded_booking_data):
    response = client.post(
        DESTINATION_PATH,
        {},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert 'Select a valid destination.' in response.content.decode()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_updates_cargo_and_refreshes_not_routed_rows(
    client, seeded_booking_data
):
    cargo = cargo_repository.find(TrackingId(TRACKING_ID))
    assert cargo is not None
    new_destination = location_repository.find(UnLocode('USNYC'))

    response = client.post(
        DESTINATION_PATH,
        {'destination': new_destination.unlocode.value},
        HTTP_HX_REQUEST='true',
    )
    updated_cargo = cargo_repository.find(cargo.tracking_id)
    dashboard_response = client.get(DASHBOARD_PATH)
    not_routed_table = (
        dashboard_response.content.decode()
        .split('id="not-routed-cargo"', 1)[1]
        .split('</section>', 1)[0]
    )

    assert response.status_code == 200
    assert response.headers['HX-Refresh'] == 'true'
    assert 'Widget for var' not in response.content.decode()
    assert updated_cargo is not None
    assert updated_cargo.route_specification.origin == cargo.route_specification.origin
    assert updated_cargo.route_specification.destination == new_destination
    assert (
        updated_cargo.route_specification.arrival_deadline
        == cargo.route_specification.arrival_deadline
    )
    assert updated_cargo.itinerary == cargo.itinerary
    assert f'data-tracking-id="{TRACKING_ID}"' in not_routed_table
    assert new_destination.name in not_routed_table


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_successful_non_htmx_updates_redirect_to_the_dashboard(client, seeded_booking_data):
    destination = location_repository.find(UnLocode('USNYC'))
    destination_response = client.post(
        DESTINATION_PATH,
        {'destination': destination.unlocode.value},
    )
    deadline_response = client.post(
        DEADLINE_PATH,
        {'deadline': '01/15/2027'},
    )

    assert destination_response.status_code == 302
    assert destination_response.url == DASHBOARD_PATH
    assert deadline_response.status_code == 302
    assert deadline_response.url == DASHBOARD_PATH


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_shows_initial_value_and_parse_error(client, seeded_booking_data):
    cargo = cargo_repository.find(TrackingId(TRACKING_ID))
    assert cargo is not None

    initial_response = client.get(DEADLINE_PATH)
    initial_content = initial_response.content.decode()
    initial_value = (
        f'{cargo.route_specification.arrival_deadline.month}/'
        f'{cargo.route_specification.arrival_deadline.day}/'
        f'{cargo.route_specification.arrival_deadline.year % 100:02d}'
    )
    invalid_response = client.post(
        DEADLINE_PATH,
        {'deadline': 'not a date'},
        HTTP_HX_REQUEST='true',
    )
    updated_cargo = cargo_repository.find(cargo.tracking_id)

    assert initial_response.status_code == 200
    assert f'value="{initial_value}"' in initial_content
    assert f'Origin: {cargo.route_specification.origin.name}' in initial_content
    assert f'Destination: {cargo.route_specification.destination.name}' in initial_content
    assert 'deadline-error' not in initial_content
    assert invalid_response.status_code == 200
    assert 'Enter a valid arrival deadline.' in invalid_response.content.decode()
    assert 'aria-invalid="true"' in invalid_response.content.decode()
    assert 'value="not a date"' in invalid_response.content.decode()
    assert updated_cargo == cargo


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_rejects_a_missing_value(client, seeded_booking_data):
    response = client.post(
        DEADLINE_PATH,
        {},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert 'Enter a valid arrival deadline.' in response.content.decode()
    assert 'value=""' in response.content.decode()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_updates_value_and_refreshes_not_routed_rows(client, seeded_booking_data):
    cargo = cargo_repository.find(TrackingId(TRACKING_ID))
    assert cargo is not None

    response = client.post(
        DEADLINE_PATH,
        {'deadline': '1/15/27'},
        HTTP_HX_REQUEST='true',
    )
    updated_cargo = cargo_repository.find(cargo.tracking_id)
    dashboard_response = client.get(DASHBOARD_PATH)
    not_routed_table = (
        dashboard_response.content.decode()
        .split('id="not-routed-cargo"', 1)[1]
        .split('</section>', 1)[0]
    )

    assert response.status_code == 200
    assert response.headers['HX-Refresh'] == 'true'
    assert 'Widget for var' not in response.content.decode()
    assert updated_cargo is not None
    assert updated_cargo.route_specification.origin == cargo.route_specification.origin
    assert updated_cargo.route_specification.destination == cargo.route_specification.destination
    assert updated_cargo.route_specification.arrival_deadline == datetime(2027, 1, 15, tzinfo=UTC)
    assert updated_cargo.itinerary == cargo.itinerary
    assert '01/15/2027' in not_routed_table


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_dialog_views_reject_unsupported_methods(client, seeded_booking_data):
    destination_response = client.put(DESTINATION_PATH)
    deadline_response = client.put(DEADLINE_PATH)

    assert destination_response.status_code == 405
    assert destination_response.headers['Allow'] == 'GET, POST'
    assert deadline_response.status_code == 405
    assert deadline_response.headers['Allow'] == 'GET, POST'


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_not_routed_rows_open_dialogs_and_unknown_cargo_errors_render(client, seeded_booking_data):
    dashboard_response = client.get(DASHBOARD_PATH)
    table_content = (
        dashboard_response.content.decode()
        .split('id="not-routed-cargo"', 1)[1]
        .split('</section>', 1)[0]
    )
    dialog_markup = (
        dashboard_response.content.decode().split('<dialog', 1)[1].split('</dialog>', 1)[0]
    )
    error_response = client.get(
        '/admin/cargo/UNKNOWN/deadline/',
        HTTP_HX_REQUEST='true',
    )

    assert dashboard_response.status_code == 200
    assert f'hx-get="/admin/cargo/{TRACKING_ID}/destination/"' in table_content
    assert f'hx-get="/admin/cargo/{TRACKING_ID}/deadline/"' in table_content
    assert 'hx-on::before-swap=' in dialog_markup
    assert error_response.status_code == 404
    assert 'Cargo with tracking ID UNKNOWN not found.' in error_response.content.decode()
    assert '<!doctype html>' not in error_response.content.decode().lower()

    full_page_error = client.get('/admin/cargo/UNKNOWN/deadline/')
    assert full_page_error.status_code == 404
    assert '<!doctype html>' in full_page_error.content.decode().lower()


@pytest.mark.django_db
def test_change_destination_use_case_rejects_the_cargo_origin(seeded_booking_data):
    cargo = cargo_repository.find(TrackingId(TRACKING_ID))
    assert cargo is not None

    with pytest.raises(ValueError, match="Origin and destination can't be the same"):
        cargo_specification.change_destination(
            cargo.tracking_id,
            cargo.route_specification.origin,
        )
