import re
from datetime import datetime

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
dialog_dashboard = CargoDashboard(cargo_repository)
dashboard_view, _ = create_booking_views(dialog_dashboard)
destination_dialog_view, deadline_dialog_view = create_booking_dialog_views(
    dialog_dashboard,
    CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
    DjangoLocationRepository().find_all,
)
urlpatterns = [
    path('admin/dashboard/', dashboard_view),
    path('admin/cargo/<str:tracking_id>/destination/', destination_dialog_view),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_dialog_view),
]


@pytest.fixture
def booking_dialog_views():
    call_command('seed_sample_data')
    cargo_repository = DjangoCargoRepository()
    locations = DjangoLocationRepository().find_all()
    views = create_booking_dialog_views(
        CargoDashboard(cargo_repository),
        CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
        lambda: locations,
    )
    return (*views, locations)


@pytest.mark.django_db
def test_not_routed_table_opens_destination_and_deadline_dialogs():
    call_command('seed_sample_data')
    cargo_repository = DjangoCargoRepository()
    dashboard, _ = create_booking_views(CargoDashboard(cargo_repository))

    content = dashboard(RequestFactory().get('/admin/dashboard/')).content.decode()
    not_routed_table = content.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]

    assert 'hx-get="/admin/cargo/DEF789/destination/"' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in not_routed_table
    assert 'hx-target="#cargo-edit-dialog-content"' in not_routed_table
    assert 'id="cargo-edit-dialog"' in not_routed_table
    assert 'Change destination' in not_routed_table
    assert 'Change deadline' in not_routed_table


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_dialog_completes_update_and_refreshes_the_not_routed_table(client):
    call_command('seed_sample_data')

    dashboard = client.get('/admin/dashboard/')
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in dashboard.content.decode()

    dialog = client.get(
        '/admin/cargo/DEF789/destination/',
        HTTP_HX_REQUEST='true',
    )
    assert dialog.status_code == 200
    assert '<!doctype html>' not in dialog.content.decode().lower()
    assert 'Melbourne' in dialog.content.decode()

    completed = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'USNYC'},
        HTTP_HX_REQUEST='true',
    )
    assert completed.status_code == 204
    assert completed['HX-Redirect'] == '/admin/dashboard/'
    assert completed.content == b''

    refreshed = client.get('/admin/dashboard/').content.decode()
    not_routed_table = refreshed.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]
    assert 'New York' in not_routed_table
    assert 'Melbourne' not in not_routed_table


@pytest.mark.django_db
def test_destination_dialog_supports_full_page_fallback_and_posts_to_its_url(
    booking_dialog_views,
):
    destination_dialog, deadline_dialog, _ = booking_dialog_views

    destination_response = destination_dialog(
        RequestFactory().get('/admin/cargo/DEF789/destination/'),
        'DEF789',
    )
    deadline_response = deadline_dialog(
        RequestFactory().get('/admin/cargo/DEF789/deadline/'),
        'DEF789',
    )
    destination_content = destination_response.content.decode()
    deadline_content = deadline_response.content.decode()

    assert destination_response.status_code == 200
    assert deadline_response.status_code == 200
    assert '<!doctype html>' in destination_content.lower()
    assert 'action="/admin/cargo/DEF789/destination/"' in destination_content
    assert 'action="/admin/cargo/DEF789/deadline/"' in deadline_content
    assert 'role="alert"' not in destination_content
    assert 'role="alert"' not in deadline_content


@pytest.mark.django_db
def test_dialog_views_reject_unsupported_methods(booking_dialog_views):
    destination_dialog, deadline_dialog, _ = booking_dialog_views

    destination_response = destination_dialog(
        RequestFactory().put('/admin/cargo/DEF789/destination/'), 'DEF789'
    )
    deadline_response = deadline_dialog(
        RequestFactory().put('/admin/cargo/DEF789/deadline/'), 'DEF789'
    )

    assert destination_response.status_code == 405
    assert destination_response['Allow'] == 'GET, POST'
    assert deadline_response.status_code == 405
    assert deadline_response['Allow'] == 'GET, POST'


@pytest.mark.django_db
def test_destination_dialog_shows_current_values_and_filters_options_without_mutating(
    booking_dialog_views,
):
    call_command('seed_sample_data')
    destination_dialog, _, locations = booking_dialog_views
    original_locations = list(locations)

    response = destination_dialog(
        RequestFactory().get(
            '/admin/cargo/DEF789/destination/',
            HTTP_HX_REQUEST='true',
        ),
        'DEF789',
    )
    content = response.content.decode()
    options = re.search(r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', content, re.DOTALL)
    original = DjangoCargoRepository().find(TrackingId('DEF789'))

    assert response.status_code == 200
    assert original is not None
    assert options is not None
    assert 'Hong Kong' in content
    assert 'Melbourne' in content
    assert 'value="CNHKG"' not in options.group(1)
    assert 'value="AUMEL"' not in options.group(1)
    assert options.group(1).count('<option') == 11
    assert locations == original_locations
    repeated = destination_dialog(
        RequestFactory().get(
            '/admin/cargo/DEF789/destination/',
            HTTP_HX_REQUEST='true',
        ),
        'DEF789',
    ).content.decode()
    repeated_options = re.search(
        r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', repeated, re.DOTALL
    )
    assert repeated_options is not None
    assert repeated_options.group(1) == options.group(1)
    assert locations == original_locations


@pytest.mark.django_db
def test_deadline_dialog_shows_current_values_and_deadline(booking_dialog_views):
    _, deadline_dialog, _ = booking_dialog_views
    call_command('seed_sample_data')
    cargo = DjangoCargoRepository().find(TrackingId('DEF789'))
    assert cargo is not None

    response = deadline_dialog(
        RequestFactory().get(
            '/admin/cargo/DEF789/deadline/',
            HTTP_HX_REQUEST='true',
        ),
        'DEF789',
    )
    content = response.content.decode()

    assert response.status_code == 200
    assert cargo.route_specification.origin.name in content
    assert cargo.route_specification.destination.name in content
    assert f'value="{cargo.route_specification.arrival_deadline.date().isoformat()}"' in content


@pytest.mark.django_db
def test_invalid_deadline_is_reported_without_changing_cargo(booking_dialog_views):
    call_command('seed_sample_data')
    _, deadline_dialog, _ = booking_dialog_views
    cargo_repository = DjangoCargoRepository()
    before = cargo_repository.find(TrackingId('DEF789'))

    response = deadline_dialog(
        RequestFactory().post(
            '/admin/cargo/DEF789/deadline/',
            {'deadline': 'not-a-date'},
            HTTP_HX_REQUEST='true',
        ),
        'DEF789',
    )
    after = cargo_repository.find(TrackingId('DEF789'))
    content = response.content.decode()

    assert response.status_code == 200
    assert (
        '<p id="deadline-error" role="alert" class="text-red-700">'
        'Enter a valid arrival deadline.</p>'
    ) in content
    assert 'aria-invalid="true"' in content
    assert 'not-a-date' in content
    assert before is not None and after is not None
    assert after.route_specification == before.route_specification


@pytest.mark.django_db
def test_missing_deadline_shows_field_error_and_keeps_empty_input(booking_dialog_views):
    call_command('seed_sample_data')
    _, deadline_dialog, _ = booking_dialog_views

    response = deadline_dialog(
        RequestFactory().post(
            '/admin/cargo/DEF789/deadline/',
            {},
            HTTP_HX_REQUEST='true',
        ),
        'DEF789',
    )
    content = response.content.decode()

    assert response.status_code == 200
    assert (
        '<p id="deadline-error" role="alert" class="text-red-700">'
        'Enter a valid arrival deadline.</p>'
    ) in content
    assert 'aria-invalid="true"' in content
    assert 'name="deadline"' in content
    assert 'value=""' in content


@pytest.mark.django_db
def test_invalid_destination_is_reported_without_changing_cargo(booking_dialog_views):
    call_command('seed_sample_data')
    destination_dialog, _, _ = booking_dialog_views
    cargo_repository = DjangoCargoRepository()
    before = cargo_repository.find(TrackingId('DEF789'))
    assert before is not None

    response = destination_dialog(
        RequestFactory().post(
            '/admin/cargo/DEF789/destination/',
            {'destination': 'CNHKG'},
            HTTP_HX_REQUEST='true',
        ),
        'DEF789',
    )
    after = cargo_repository.find(TrackingId('DEF789'))
    content = response.content.decode()

    assert response.status_code == 200
    assert (
        '<p id="destination-error" role="alert" class="text-red-700">'
        'Select a valid destination.</p>'
    ) in content
    assert 'aria-invalid="true"' in content
    assert before.route_specification == after.route_specification


@pytest.mark.django_db
def test_destination_update_preserves_other_specification_fields(booking_dialog_views):
    call_command('seed_sample_data')
    destination_dialog, _, _ = booking_dialog_views
    cargo_repository = DjangoCargoRepository()
    before = cargo_repository.find(TrackingId('DEF789'))
    assert before is not None

    response = destination_dialog(
        RequestFactory().post(
            '/admin/cargo/DEF789/destination/',
            {'destination': 'USNYC'},
        ),
        'DEF789',
    )
    after = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 302
    assert response['Location'] == '/admin/dashboard/'
    assert after is not None
    assert after.route_specification.origin == before.route_specification.origin
    assert after.route_specification.arrival_deadline == before.route_specification.arrival_deadline
    assert after.route_specification.destination.unlocode.value == 'USNYC'
    dashboard, _ = create_booking_views(CargoDashboard(cargo_repository))
    refreshed = dashboard(RequestFactory().get('/admin/dashboard/')).content.decode()
    not_routed_table = refreshed.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]
    assert 'New York' in not_routed_table


@pytest.mark.django_db
def test_deadline_update_preserves_route_specification_and_redirects_htmx(
    booking_dialog_views,
):
    call_command('seed_sample_data')
    _, deadline_dialog, _ = booking_dialog_views
    cargo_repository = DjangoCargoRepository()
    before = cargo_repository.find(TrackingId('DEF789'))
    assert before is not None
    new_deadline = datetime.fromisoformat('2026-11-09T00:00:00+00:00')

    response = deadline_dialog(
        RequestFactory().post(
            '/admin/cargo/DEF789/deadline/',
            {'deadline': '2026-11-09'},
            HTTP_HX_REQUEST='true',
        ),
        'DEF789',
    )
    after = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 204
    assert response['HX-Redirect'] == '/admin/dashboard/'
    assert after is not None
    assert after.route_specification.origin == before.route_specification.origin
    assert after.route_specification.destination == before.route_specification.destination
    assert after.route_specification.arrival_deadline == new_deadline
