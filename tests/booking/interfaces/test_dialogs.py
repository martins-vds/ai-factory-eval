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
from cargotracker.location.infrastructure.repository import DjangoLocationRepository

cargo_repository = DjangoCargoRepository()
location_repository = DjangoLocationRepository()
locations_for_dialogs = []
dashboard = CargoDashboard(cargo_repository)
specification = CargoSpecification(
    cargo_repository,
    DjangoHandlingEventRepository(),
)
destination_dialog_view, deadline_dialog_view = create_booking_dialog_views(
    dashboard,
    specification,
    lambda: locations_for_dialogs,
)
dashboard_view, cargo_details_view = create_booking_views(dashboard)

urlpatterns = [
    path('admin/dashboard/', dashboard_view),
    path('admin/cargo/<str:tracking_id>/', cargo_details_view),
    path('admin/cargo/<str:tracking_id>/destination/', destination_dialog_view),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_dialog_view),
]


@pytest.fixture(autouse=True)
def clear_location_list():
    locations_for_dialogs.clear()


def _seed_booking_data():
    call_command('seed_sample_data')
    locations_for_dialogs.extend(location_repository.find_all())


def _select_options(content):
    match = re.search(
        r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>',
        content,
        re.DOTALL,
    )
    assert match is not None
    return match.group(1)


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_not_routed_table_opens_destination_and_deadline_dialogs(client):
    _seed_booking_data()

    content = client.get('/admin/dashboard/').content.decode()
    not_routed_table = content.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]

    assert 'hx-get="/admin/cargo/DEF789/destination/"' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in not_routed_table
    assert 'id="cargo-edit-dialog"' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_shows_current_specification_and_stable_filtered_options(client):
    _seed_booking_data()
    original_location_codes = [location.unlocode.value for location in locations_for_dialogs]

    first = client.get('/admin/cargo/DEF789/destination/', HTTP_HX_REQUEST='true')
    first_content = first.content.decode()
    first_options = _select_options(first_content)
    second = client.get('/admin/cargo/DEF789/destination/', HTTP_HX_REQUEST='true')
    second_options = _select_options(second.content.decode())

    assert first.status_code == 200
    assert 'Hong Kong' in first_content
    assert 'Melbourne' in first_content
    assert 'value="CNHKG"' not in first_options
    assert 'value="AUMEL"' not in first_options
    assert 'value="USDAL"' in first_options
    assert '<option value="" disabled selected>Choose a destination</option>' in first_options
    assert first_options == second_options
    assert [
        location.unlocode.value for location in locations_for_dialogs
    ] == original_location_codes
    assert '<html' not in first_content.lower()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_shows_the_existing_value(client):
    _seed_booking_data()
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    current_deadline = cargo.route_specification.arrival_deadline.date().isoformat()

    response = client.get('/admin/cargo/DEF789/deadline/', HTTP_HX_REQUEST='true')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Hong Kong' in content
    assert 'Melbourne' in content
    assert re.search(r'<input\b[^>]*name="deadline"[^>]*>', content)
    assert f'value="{current_deadline}"' in content
    assert '<html' not in content.lower()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_invalid_destination_is_reported_without_changing_cargo(client):
    _seed_booking_data()
    cargo_before = cargo_repository.find(TrackingId('DEF789'))
    assert cargo_before is not None

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'CNHKG'},
        HTTP_HX_REQUEST='true',
    )
    cargo_after = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 200
    content = response.content.decode()
    assert 'Select a valid destination.' in content
    assert '<html' not in content.lower()
    assert cargo_after == cargo_before


@pytest.mark.django_db
def test_application_rejects_destination_matching_origin():
    _seed_booking_data()
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None

    with pytest.raises(ValueError, match="Origin and destination can't be the same"):
        specification.change_destination(
            cargo.tracking_id,
            cargo.route_specification.origin,
        )


@pytest.mark.django_db
@pytest.mark.xfail(
    strict=True,
    reason='The application use case accepts a destination excluded from the dialog options.',
)
def test_application_rejects_current_destination_not_offered():
    _seed_booking_data()
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None

    with pytest.raises(ValueError):
        specification.change_destination(
            cargo.tracking_id,
            cargo.route_specification.destination,
        )


@pytest.mark.django_db
def test_application_rejects_unparsed_deadline_value():
    _seed_booking_data()

    with pytest.raises(TypeError, match='Arrival deadline must be a datetime'):
        specification.change_deadline(TrackingId('DEF789'), '2026-99-99')


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_invalid_deadline_shows_field_error_and_keeps_cargo_unchanged(client):
    _seed_booking_data()
    cargo_before = cargo_repository.find(TrackingId('DEF789'))
    assert cargo_before is not None

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': '2026-99-99'},
        HTTP_HX_REQUEST='true',
    )
    cargo_after = cargo_repository.find(TrackingId('DEF789'))
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Enter a valid arrival deadline.' in content
    assert 'aria-invalid="true"' in content
    assert 'aria-describedby="deadline-error"' in content
    assert '<html' not in content.lower()
    assert cargo_after == cargo_before


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_update_completes_dialog_and_refreshes_table(client):
    _seed_booking_data()
    cargo_before = cargo_repository.find(TrackingId('DEF789'))
    assert cargo_before is not None

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'USDAL'},
        HTTP_HX_REQUEST='true',
    )
    cargo_after = cargo_repository.find(TrackingId('DEF789'))
    refreshed_dashboard = client.get('/admin/dashboard/').content.decode()
    not_routed_table = refreshed_dashboard.split('id="not-routed-cargo"', 1)[1].split(
        '</section>', 1
    )[0]

    assert response.status_code == 204
    assert response['HX-Redirect'] == '/admin/dashboard/'
    assert b'Widget for var' not in response.content
    assert cargo_after is not None
    assert cargo_after.route_specification.origin == cargo_before.route_specification.origin
    assert (
        cargo_after.route_specification.arrival_deadline
        == cargo_before.route_specification.arrival_deadline
    )
    assert cargo_after.route_specification.destination.unlocode.value == 'USDAL'
    assert 'Dallas' in not_routed_table
    assert 'Melbourne' not in not_routed_table


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_update_completes_dialog_and_refreshes_table(client):
    _seed_booking_data()
    cargo_before = cargo_repository.find(TrackingId('DEF789'))
    assert cargo_before is not None
    new_deadline = datetime(2030, 4, 5, tzinfo=UTC)

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': '2030-04-05'},
        HTTP_HX_REQUEST='true',
    )
    cargo_after = cargo_repository.find(TrackingId('DEF789'))
    refreshed_dashboard = client.get('/admin/dashboard/').content.decode()
    not_routed_table = refreshed_dashboard.split('id="not-routed-cargo"', 1)[1].split(
        '</section>', 1
    )[0]

    assert response.status_code == 204
    assert response['HX-Redirect'] == '/admin/dashboard/'
    assert b'Widget for var' not in response.content
    assert cargo_after is not None
    assert cargo_after.route_specification.origin == cargo_before.route_specification.origin
    assert (
        cargo_after.route_specification.destination == cargo_before.route_specification.destination
    )
    assert cargo_after.route_specification.arrival_deadline == new_deadline
    assert '04/05/2030' in not_routed_table


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_dialog_pages_render_form_actions_without_errors(client):
    _seed_booking_data()

    destination = client.get('/admin/cargo/DEF789/destination/')
    deadline = client.get('/admin/cargo/DEF789/deadline/')

    assert destination.status_code == 200
    assert 'action="/admin/cargo/DEF789/destination/"' in destination.content.decode()
    assert 'role="alert"' not in destination.content.decode()
    assert 'value="USDAL"' in _select_options(destination.content.decode())
    assert '<option value="" disabled selected>Choose a destination</option>' in _select_options(
        destination.content.decode()
    )
    assert '<html' in destination.content.decode().lower()
    assert deadline.status_code == 200
    assert 'action="/admin/cargo/DEF789/deadline/"' in deadline.content.decode()
    assert 'role="alert"' not in deadline.content.decode()
    assert '<html' in deadline.content.decode().lower()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_dialogs_only_allow_get_and_post(client):
    _seed_booking_data()

    for endpoint in ('destination', 'deadline'):
        response = client.put(f'/admin/cargo/DEF789/{endpoint}/')

        assert response.status_code == 405
        assert response['Allow'] == 'GET, POST'


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_missing_dialog_values_show_field_errors(client):
    _seed_booking_data()

    destination = client.post(
        '/admin/cargo/DEF789/destination/',
        {},
        HTTP_HX_REQUEST='true',
    )
    deadline = client.post(
        '/admin/cargo/DEF789/deadline/',
        {},
        HTTP_HX_REQUEST='true',
    )
    destination_content = destination.content.decode()
    deadline_content = deadline.content.decode()

    assert destination.status_code == 200
    assert 'Select a valid destination.' in destination_content
    assert 'aria-describedby="destination-error"' in destination_content
    assert 'aria-invalid="true"' in destination_content
    assert '<option value="" disabled selected>Choose a destination</option>' in destination_content
    assert deadline.status_code == 200
    assert 'Enter a valid arrival deadline.' in deadline_content
    assert 'aria-describedby="deadline-error"' in deadline_content
    assert 'aria-invalid="true"' in deadline_content
    assert 'value=""' in deadline_content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_dialogs_return_not_found_for_unknown_cargo(client):
    _seed_booking_data()

    assert client.get('/admin/cargo/UNKNOWN/destination/').status_code == 404
    assert client.get('/admin/cargo/UNKNOWN/deadline/').status_code == 404


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_non_htmx_updates_redirect_to_dashboard(client):
    _seed_booking_data()

    destination = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'USDAL'},
    )
    deadline = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': '2030-04-05'},
    )

    assert destination.status_code == 302
    assert destination['Location'] == '/admin/dashboard/'
    assert deadline.status_code == 302
    assert deadline['Location'] == '/admin/dashboard/'
