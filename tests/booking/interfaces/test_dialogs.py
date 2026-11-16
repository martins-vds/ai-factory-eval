import re

import pytest
from django.core.management import call_command
from django.http import Http404
from django.test import RequestFactory, override_settings
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
cargo_dashboard = CargoDashboard(cargo_repository)
dashboard_view, _ = create_booking_views(cargo_dashboard)
specification = CargoSpecification(cargo_repository, DjangoHandlingEventRepository())


def _available_locations():
    return available_locations


destination_dialog_view = create_destination_dialog_view(
    specification,
    cargo_dashboard,
    _available_locations,
)
deadline_dialog_view = create_deadline_dialog_view(specification, cargo_dashboard)
urlpatterns = [
    path('admin/dashboard/', dashboard_view),
    path(
        'admin/cargo/<str:tracking_id>/destination-dialog/',
        destination_dialog_view,
    ),
    path(
        'admin/cargo/<str:tracking_id>/deadline-dialog/',
        deadline_dialog_view,
    ),
]


@pytest.fixture(autouse=True)
def reset_sample_data():
    call_command('seed_sample_data')
    available_locations[:] = location_repository.find_all()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_not_routed_table_offers_destination_and_deadline_dialog_openers(client):
    response = client.get('/admin/dashboard/')
    content = response.content.decode()
    not_routed_table = content.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]

    assert response.status_code == 200
    assert 'data-tracking-id="DEF789"' in not_routed_table
    assert 'href="/admin/cargo/DEF789/route/"' in not_routed_table
    assert 'href="/admin/cargo/DEF789/destination-dialog/"' in not_routed_table
    assert 'href="/admin/cargo/DEF789/deadline-dialog/"' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/destination-dialog/"' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/deadline-dialog/"' in not_routed_table
    assert 'id="dialog-container"' in not_routed_table
    assert 'hx-on::after-swap=' in not_routed_table
    assert 'hx-trigger="cargoUpdated from:body"' in not_routed_table


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_has_a_native_no_javascript_fallback(client):
    response = client.get('/admin/cargo/DEF789/destination-dialog/')
    content = response.content.decode()

    assert response.status_code == 200
    assert '<!doctype html>' in content
    assert re.search(r'<dialog\b[^>]*\bopen(?:\s|>)', content)
    assert 'method="dialog"' in content
    assert '<noscript>' in content
    assert 'href="/admin/dashboard/"' in content


@pytest.mark.django_db
def test_destination_dialog_reports_unknown_cargo():
    request = RequestFactory().get('/admin/cargo/MISSING1/destination-dialog/')

    with pytest.raises(
        Http404,
        match=r'^Cargo with tracking ID MISSING1 not found\.$',
    ):
        destination_dialog_view(request, 'MISSING1')


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_shows_current_values_and_stable_filtered_options(client):
    original_codes = tuple(location.unlocode.value for location in available_locations)

    first_response = client.get(
        '/admin/cargo/DEF789/destination-dialog/',
        HTTP_HX_REQUEST='true',
    )
    second_response = client.get(
        '/admin/cargo/DEF789/destination-dialog/',
        HTTP_HX_REQUEST='true',
    )
    first_content = first_response.content.decode()
    second_content = second_response.content.decode()
    options = re.search(
        r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>',
        first_content,
        re.DOTALL,
    )
    second_options = re.search(
        r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>',
        second_content,
        re.DOTALL,
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert 'aria-labelledby="destination-dialog-title"' in first_content
    assert 'Hong Kong' in first_content and 'Melbourne' in first_content
    assert 'destination-error' not in first_content
    assert options is not None
    assert 'value="CNHKG"' not in options.group(1)
    assert 'value="AUMEL"' not in options.group(1)
    assert 'value="USNYC"' in options.group(1)
    assert tuple(location.unlocode.value for location in available_locations) == original_codes
    assert second_options is not None
    assert options.group(1) == second_options.group(1)


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_update_preserves_other_specification_fields_and_refreshes_table(client):
    original = cargo_repository.find(TrackingId('DEF789'))
    assert original is not None

    response = client.post(
        '/admin/cargo/DEF789/destination-dialog/',
        {'destination': 'USNYC'},
        HTTP_HX_REQUEST='true',
    )
    updated = cargo_repository.find(TrackingId('DEF789'))
    dashboard = client.get('/admin/dashboard/').content.decode()
    not_routed_table = dashboard.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]

    assert response.status_code == 200
    assert response.headers['HX-Trigger'] == 'cargoUpdated'
    assert b'Widget' not in response.content
    assert updated is not None
    assert updated.route_specification.origin == original.route_specification.origin
    assert updated.route_specification.destination.unlocode.value == 'USNYC'
    assert (
        updated.route_specification.arrival_deadline
        == original.route_specification.arrival_deadline
    )
    assert 'New York' in not_routed_table
    assert 'USNYC' in not_routed_table


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_update_rejects_origin_and_leaves_cargo_unchanged(client):
    original = cargo_repository.find(TrackingId('DEF789'))
    assert original is not None

    response = client.post(
        '/admin/cargo/DEF789/destination-dialog/',
        {'destination': 'CNHKG'},
        HTTP_HX_REQUEST='true',
    )
    updated = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 200
    assert (
        '<p id="destination-error" class="mt-2 text-red-800" role="alert">'
        'Select a valid destination.</p>'
    ) in response.content.decode()
    assert 'aria-invalid="true"' in response.content.decode()
    assert updated is not None
    assert updated.route_specification == original.route_specification


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_update_redirects_after_non_htmx_submission(client):
    response = client.post(
        '/admin/cargo/DEF789/destination-dialog/',
        {'destination': 'USNYC'},
    )

    assert response.status_code == 302
    assert response.url == '/admin/dashboard/'


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_shows_current_specification_values(client):
    original = cargo_repository.find(TrackingId('DEF789'))
    assert original is not None

    response = client.get(
        '/admin/cargo/DEF789/deadline-dialog/',
        HTTP_HX_REQUEST='true',
    )
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Hong Kong' in content and 'Melbourne' in content
    assert 'deadline-error' not in content
    expected_deadline = original.route_specification.arrival_deadline.date().isoformat()
    assert re.search(
        rf'<input\b(?=[^>]*name="deadline")(?=[^>]*value="{expected_deadline}")',
        content,
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_unparseable_deadline_shows_field_error_without_updating_cargo(client):
    original = cargo_repository.find(TrackingId('DEF789'))
    assert original is not None

    response = client.post(
        '/admin/cargo/DEF789/deadline-dialog/',
        {'deadline': 'not-a-date'},
        HTTP_HX_REQUEST='true',
    )
    content = response.content.decode()
    updated = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 200
    assert (
        '<p id="deadline-error" class="mt-2 text-red-800" role="alert">'
        'Enter a valid arrival deadline.</p>'
    ) in content
    assert 'aria-invalid="true"' in content
    assert updated is not None
    assert (
        updated.route_specification.arrival_deadline
        == original.route_specification.arrival_deadline
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_missing_deadline_keeps_empty_field_and_shows_field_error(client):
    response = client.post(
        '/admin/cargo/DEF789/deadline-dialog/',
        {},
        HTTP_HX_REQUEST='true',
    )
    content = response.content.decode()

    assert response.status_code == 200
    assert (
        '<p id="deadline-error" class="mt-2 text-red-800" role="alert">'
        'Enter a valid arrival deadline.</p>'
    ) in content
    assert re.search(r'<input\b(?=[^>]*name="deadline")(?=[^>]*value="")', content)


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_update_preserves_other_specification_fields_and_refreshes_table(client):
    original = cargo_repository.find(TrackingId('DEF789'))
    assert original is not None

    response = client.post(
        '/admin/cargo/DEF789/deadline-dialog/',
        {'deadline': '2030-12-11'},
        HTTP_HX_REQUEST='true',
    )
    updated = cargo_repository.find(TrackingId('DEF789'))
    dashboard = client.get('/admin/dashboard/').content.decode()
    not_routed_table = dashboard.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]

    assert response.status_code == 200
    assert response.headers['HX-Trigger'] == 'cargoUpdated'
    assert b'Widget' not in response.content
    assert updated is not None
    assert updated.route_specification.origin == original.route_specification.origin
    assert updated.route_specification.destination == original.route_specification.destination
    assert updated.route_specification.arrival_deadline.isoformat() == '2030-12-11T00:00:00+00:00'
    assert '12/11/2030' in not_routed_table
