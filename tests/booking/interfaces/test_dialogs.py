import re

import pytest
from django.core.management import call_command
from django.http import Http404
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
location_repository = DjangoLocationRepository()
cargo_dashboard = CargoDashboard(cargo_repository)
available_locations = []
destination_dialog_view, deadline_dialog_view = create_dialog_views(
    cargo_dashboard,
    CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
    lambda: available_locations,
)
dashboard_view, _ = create_booking_views(cargo_dashboard)
urlpatterns = [
    path('admin/dashboard/', dashboard_view),
    path('admin/cargo/<str:tracking_id>/destination/', destination_dialog_view),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_dialog_view),
]


@pytest.fixture
def sample_bookings():
    call_command('seed_sample_data')
    available_locations[:] = location_repository.find_all()
    yield
    available_locations.clear()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_dashboard_opens_destination_and_deadline_dialogs_from_not_routed_rows(
    client, sample_bookings
):
    response = client.get('/admin/dashboard/')
    content = response.content.decode()
    not_routed_table = content.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]

    assert response.status_code == 200
    assert 'data-tracking-id="DEF789"' in not_routed_table
    assert 'Hong Kong' in not_routed_table and 'Melbourne' in not_routed_table
    assert 'href="/admin/cargo/DEF789/route/"' in not_routed_table
    assert 'href="/admin/cargo/DEF789/destination/"' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in not_routed_table
    assert 'aria-haspopup="dialog"' in not_routed_table
    assert 'href="/admin/cargo/DEF789/deadline/"' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in not_routed_table
    assert 'id="cargo-edit-dialog"' in content
    assert 'id="cargo-edit-dialog-title"' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_shows_current_values_and_stable_filtered_options(
    client, sample_bookings
):
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    original_locations = list(available_locations)
    url = '/admin/cargo/DEF789/destination/'

    first = client.get(url, HTTP_HX_REQUEST='true')
    second = client.get(url, HTTP_HX_REQUEST='true')
    content = first.content.decode()
    options = re.search(r'<select\b[^>]*>(.*?)</select>', content, re.DOTALL)
    second_options = re.search(r'<select\b[^>]*>(.*?)</select>', second.content.decode(), re.DOTALL)
    assert options is not None
    assert second_options is not None
    first_option = re.search(r'<option\b[^>]*selected', options.group(1))
    first_destination = next(
        location
        for location in available_locations
        if location not in (cargo.route_specification.origin, cargo.route_specification.destination)
    )

    assert first.status_code == 200
    assert '<html' not in content
    fallback = client.get(url)
    assert fallback.status_code == 200
    assert '<html lang="en">' in fallback.content.decode()
    assert cargo.route_specification.origin.name in content
    assert cargo.route_specification.destination.name in content
    assert cargo.route_specification.origin.unlocode.value not in options.group(1)
    assert cargo.route_specification.destination.unlocode.value not in options.group(1)
    assert first_option is not None
    assert f'value="{first_destination.unlocode.value}" selected' in options.group(1)
    assert 'aria-invalid="true"' not in content
    assert options.group(1) == second_options.group(1)
    assert available_locations == original_locations


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
@pytest.mark.parametrize(
    ('url', 'title'),
    (
        ('/admin/cargo/DEF789/destination/', 'Change destination for cargo DEF789'),
        ('/admin/cargo/DEF789/deadline/', 'Change arrival deadline for cargo DEF789'),
    ),
)
def test_dialogs_render_full_pages_without_htmx(client, sample_bookings, url, title):
    response = client.get(url)

    assert response.status_code == 200
    assert '<html lang="en">' in response.content.decode()
    assert title in response.content.decode()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_handles_empty_options(client, sample_bookings):
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    available_locations[:] = [
        cargo.route_specification.origin,
        cargo.route_specification.destination,
    ]

    response = client.get('/admin/cargo/DEF789/destination/', HTTP_HX_REQUEST='true')
    content = response.content.decode()
    options = re.search(r'<select\b[^>]*>(.*?)</select>', content, re.DOTALL)
    assert options is not None

    assert response.status_code == 200
    assert '<option value="" disabled selected>Choose a destination</option>' in options.group(1)
    assert options.group(1).count('<option') == 1


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
@pytest.mark.parametrize(
    'url',
    (
        '/admin/cargo/UNKNOWN/destination/',
        '/admin/cargo/UNKNOWN/deadline/',
    ),
)
def test_unknown_cargo_dialog_returns_not_found(client, sample_bookings, url):
    response = client.get(url, HTTP_HX_REQUEST='true')
    dialog = destination_dialog_view if url.endswith('/destination/') else deadline_dialog_view

    assert response.status_code == 404
    with pytest.raises(Http404) as exception:
        dialog(RequestFactory().get(url), 'UNKNOWN')
    assert str(exception.value) == 'Cargo with tracking ID UNKNOWN not found.'


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
@pytest.mark.parametrize(
    ('dialog', 'url'),
    (
        (destination_dialog_view, '/admin/cargo/DEF789/destination/'),
        (deadline_dialog_view, '/admin/cargo/DEF789/deadline/'),
    ),
)
def test_dialogs_reject_unsupported_methods(sample_bookings, dialog, url):
    response = dialog(RequestFactory().put(url), 'DEF789')

    assert response.status_code == 405
    assert response['Allow'] == 'GET, POST'


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_rejects_unavailable_destination(client, sample_bookings):
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': cargo.route_specification.origin.unlocode.value},
        HTTP_HX_REQUEST='true',
    )
    updated = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 200
    assert (
        '<p class="mb-2 text-red-700" id="destination-error" role="alert">'
        'Select a valid destination.</p>'
    ) in response.content.decode()
    assert updated is not None
    assert updated.route_specification == cargo.route_specification


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_rejects_missing_destination(client, sample_bookings):
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {},
        HTTP_HX_REQUEST='true',
    )
    updated = cargo_repository.find(TrackingId('DEF789'))
    content = response.content.decode()

    assert response.status_code == 200
    assert (
        '<p class="mb-2 text-red-700" id="destination-error" role="alert">'
        'Select a valid destination.</p>'
    ) in content
    assert '<option value="" disabled selected>Choose a destination</option>' in content
    assert updated is not None
    assert updated.route_specification == cargo.route_specification


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_updates_cargo_and_refreshes_the_dashboard(client, sample_bookings):
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    new_destination = next(
        location
        for location in available_locations
        if location not in (cargo.route_specification.origin, cargo.route_specification.destination)
    )

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': new_destination.unlocode.value},
        HTTP_HX_REQUEST='true',
    )
    updated = cargo_repository.find(TrackingId('DEF789'))
    dashboard = client.get('/admin/dashboard/').content.decode()
    not_routed_table = dashboard.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]

    assert response.status_code == 204
    assert response['HX-Redirect'] == '/admin/dashboard/'
    assert updated is not None
    assert updated.route_specification.origin == cargo.route_specification.origin
    assert updated.route_specification.destination == new_destination
    assert (
        updated.route_specification.arrival_deadline == cargo.route_specification.arrival_deadline
    )
    assert new_destination.name in not_routed_table
    assert new_destination.unlocode.value in not_routed_table
    assert 'data-tracking-id="DEF789"' in not_routed_table


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_redirects_after_non_htmx_update(client, sample_bookings):
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    new_destination = next(
        location
        for location in available_locations
        if location not in (cargo.route_specification.origin, cargo.route_specification.destination)
    )

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': new_destination.unlocode.value},
    )

    assert response.status_code == 302
    assert response.url == '/admin/dashboard/'


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_shows_initial_value_and_parse_error(client, sample_bookings):
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    url = '/admin/cargo/DEF789/deadline/'
    initial = client.get(url, HTTP_HX_REQUEST='true').content.decode()

    response = client.post(
        url,
        {'deadline': 'not-a-date'},
        HTTP_HX_REQUEST='true',
    )
    content = response.content.decode()
    updated = cargo_repository.find(TrackingId('DEF789'))
    deadline_input = re.search(r'<input\b[^>]*name="deadline"[^>]*>', initial, re.DOTALL)

    assert deadline_input is not None
    assert (
        f'value="{cargo.route_specification.arrival_deadline:%Y-%m-%d}"' in deadline_input.group()
    )
    assert response.status_code == 200
    assert '<html' not in initial
    assert (
        '<p class="mb-2 text-red-700" id="deadline-error" role="alert">'
        'Enter a valid arrival deadline.</p>'
    ) in content
    assert 'aria-invalid="true"' in content
    assert 'value="not-a-date"' in content
    assert updated is not None
    assert updated.route_specification == cargo.route_specification


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_updates_cargo_and_refreshes_the_dashboard(client, sample_bookings):
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    new_deadline = '2030-11-12'

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': new_deadline},
        HTTP_HX_REQUEST='true',
    )
    updated = cargo_repository.find(TrackingId('DEF789'))
    dashboard = client.get('/admin/dashboard/').content.decode()
    not_routed_table = dashboard.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]

    assert response.status_code == 204
    assert response['HX-Redirect'] == '/admin/dashboard/'
    assert updated is not None
    assert updated.route_specification.origin == cargo.route_specification.origin
    assert updated.route_specification.destination == cargo.route_specification.destination
    assert updated.route_specification.arrival_deadline.date().isoformat() == new_deadline
    assert '11/12/2030' in not_routed_table
    assert 'data-tracking-id="DEF789"' in not_routed_table


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_rejects_missing_deadline(client, sample_bookings):
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {},
        HTTP_HX_REQUEST='true',
    )
    updated = cargo_repository.find(TrackingId('DEF789'))
    content = response.content.decode()

    assert response.status_code == 200
    assert (
        '<p class="mb-2 text-red-700" id="deadline-error" role="alert">'
        'Enter a valid arrival deadline.</p>'
    ) in content
    assert 'value=""' in content
    assert updated is not None
    assert updated.route_specification == cargo.route_specification
