import re

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

locations = []
cargo_repository = DjangoCargoRepository()
dashboard_view, _ = create_booking_views(CargoDashboard(cargo_repository))
destination_dialog = create_destination_dialog_view(
    CargoDashboard(cargo_repository),
    CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
    lambda: locations,
)
deadline_dialog = create_deadline_dialog_view(
    CargoDashboard(cargo_repository),
    CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
)
urlpatterns = [
    path('admin/dashboard/', dashboard_view),
    path('admin/cargo/<str:tracking_id>/destination/', destination_dialog),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_dialog),
]


@pytest.fixture
def sample_booking():
    call_command('seed_sample_data')
    locations[:] = DjangoLocationRepository().find_all()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_shows_current_specification_and_filters_choices(client, sample_booking):
    response = client.get('/admin/cargo/DEF789/destination/')

    content = response.content.decode()
    options = re.search(r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', content, re.DOTALL)

    assert response.status_code == 200
    assert 'Hong Kong' in content
    assert 'Melbourne' in content
    assert options is not None
    assert 'value="CNHKG"' not in options.group(1)
    assert 'value="AUMEL"' not in options.group(1)
    assert 'value="USCHI"' in options.group(1)


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_update_preserves_other_fields_and_refreshes_dashboard(client, sample_booking):
    before = cargo_repository.find(TrackingId('DEF789'))
    assert before is not None

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'USCHI'},
        HTTP_HX_REQUEST='true',
    )

    updated = cargo_repository.find(TrackingId('DEF789'))
    assert response.status_code == 204
    assert response.headers['HX-Redirect'] == '/admin/dashboard/'
    assert response.content == b''
    assert updated is not None
    assert updated.route_specification.origin == before.route_specification.origin
    assert updated.route_specification.destination.unlocode.value == 'USCHI'
    assert (
        updated.route_specification.arrival_deadline == before.route_specification.arrival_deadline
    )

    dashboard = client.get('/admin/dashboard/').content.decode()
    not_routed = dashboard.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]
    cargo_row = not_routed.split('data-tracking-id="DEF789"', 1)[1].split('</tr>', 1)[0]
    assert 'USCHI' in cargo_row
    assert 'AUMEL' not in cargo_row


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_update_redirects_after_a_regular_form_submit(client, sample_booking):
    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'USCHI'},
    )

    updated = cargo_repository.find(TrackingId('DEF789'))
    assert response.status_code == 302
    assert response['Location'] == '/admin/dashboard/'
    assert updated is not None
    assert updated.route_specification.destination.unlocode.value == 'USCHI'


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_shows_current_specification(client, sample_booking):
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    deadline = cargo.route_specification.arrival_deadline.strftime('%Y-%m-%d')

    response = client.get('/admin/cargo/DEF789/deadline/')

    content = response.content.decode()
    assert response.status_code == 200
    assert 'Hong Kong' in content
    assert 'Melbourne' in content
    assert 'name="deadline"' in content
    assert f'value="{deadline}"' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_invalid_deadline_is_reported_at_the_field_without_changing_cargo(client, sample_booking):
    before = cargo_repository.find(TrackingId('DEF789'))
    assert before is not None

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': 'not-a-date'},
        HTTP_HX_REQUEST='true',
    )

    content = response.content.decode()
    after = cargo_repository.find(TrackingId('DEF789'))
    assert response.status_code == 400
    assert 'id="deadline-error" role="alert">Enter a valid arrival deadline.</p>' in content
    assert 'Origin: Hong Kong.' in content
    assert 'Destination: Melbourne.' in content
    assert 'action="/admin/cargo/DEF789/deadline/"' in content
    assert 'value="not-a-date"' in content
    assert 'aria-invalid="true"' in content
    assert after == before


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_missing_deadline_is_reported_at_the_field(client, sample_booking):
    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {},
        HTTP_HX_REQUEST='true',
    )

    content = response.content.decode()
    assert response.status_code == 400
    assert 'id="deadline-error" role="alert">Enter a valid arrival deadline.</p>' in content
    assert 'name="deadline"' in content
    assert 'value=""' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_update_preserves_route_and_completes_the_dialog(client, sample_booking):
    before = cargo_repository.find(TrackingId('DEF789'))
    assert before is not None

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': '2099-12-31'},
        HTTP_HX_REQUEST='true',
    )

    updated = cargo_repository.find(TrackingId('DEF789'))
    assert response.status_code == 204
    assert response.headers['HX-Redirect'] == '/admin/dashboard/'
    assert response.content == b''
    assert updated is not None
    assert updated.route_specification.origin == before.route_specification.origin
    assert updated.route_specification.destination == before.route_specification.destination
    assert updated.route_specification.arrival_deadline.strftime('%Y-%m-%d') == '2099-12-31'
    dashboard = client.get('/admin/dashboard/').content.decode()
    not_routed = dashboard.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]
    cargo_row = not_routed.split('data-tracking-id="DEF789"', 1)[1].split('</tr>', 1)[0]
    assert '12/31/2099' in cargo_row


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_choices_are_stable_across_renders_without_mutating_locations(
    client, sample_booking
):
    original_locations = list(locations)
    first = client.get('/admin/cargo/DEF789/destination/').content.decode()
    second = client.get('/admin/cargo/DEF789/destination/').content.decode()
    pattern = r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>'
    first_options = re.search(pattern, first, re.DOTALL)
    second_options = re.search(pattern, second, re.DOTALL)

    assert first_options is not None
    assert second_options is not None
    assert locations == original_locations
    assert re.findall(r'<option\b[^>]*value="([^"]+)"', first_options.group(1)) == re.findall(
        r'<option\b[^>]*value="([^"]+)"', second_options.group(1)
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_dashboard_opens_destination_and_deadline_dialogs_for_not_routed_cargo(
    client, sample_booking
):
    response = client.get('/admin/dashboard/')
    content = response.content.decode()
    not_routed = content.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]

    assert response.status_code == 200
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in not_routed
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in not_routed
    assert 'id="cargo-edit-dialog"' in not_routed


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_rejects_a_location_outside_its_choices(client, sample_booking):
    before = cargo_repository.find(TrackingId('DEF789'))
    assert before is not None

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'CNHKG'},
        HTTP_HX_REQUEST='true',
    )

    after = cargo_repository.find(TrackingId('DEF789'))
    content = response.content.decode()
    assert response.status_code == 400
    assert 'id="destination-error" role="alert">Select a valid destination.</p>' in content
    assert 'Origin: Hong Kong.' in content
    assert 'Current destination: Melbourne.' in content
    assert 'value="USCHI"' in content
    assert 'aria-invalid="true"' in content
    assert after == before


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
@pytest.mark.parametrize(
    'url',
    (
        '/admin/cargo/MISSING/destination/',
        '/admin/cargo/MISSING/deadline/',
    ),
)
def test_dialog_for_unknown_cargo_renders_not_found_response(client, sample_booking, url):
    response = client.get(url, HTTP_HX_REQUEST='true')

    assert response.status_code == 404
    assert b'Cargo MISSING was not found.' in response.content
