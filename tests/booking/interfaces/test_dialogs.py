import re
from datetime import UTC, datetime

import pytest
from django.core.management import call_command
from django.http import Http404
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
specification = CargoSpecification(cargo_repository, DjangoHandlingEventRepository())
dashboard_view, _ = create_booking_views(CargoDashboard(cargo_repository))
destination_dialog_view, deadline_dialog_view = create_booking_dialog_views(
    cargo_repository,
    location_repository,
    specification,
)

urlpatterns = [
    path('admin/dashboard/', dashboard_view),
    path(
        'admin/cargo/<str:tracking_id>/destination/',
        destination_dialog_view,
    ),
    path(
        'admin/cargo/<str:tracking_id>/deadline/',
        deadline_dialog_view,
    ),
]


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_not_routed_table_opens_destination_and_deadline_dialogs(client):
    call_command('seed_sample_data')

    response = client.get('/admin/dashboard/')
    content = response.content.decode()

    assert 'hx-get="/admin/cargo/DEF789/destination/"' in content
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in content
    assert 'href="/admin/cargo/DEF789/route/"' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_shows_current_values_and_stable_filtered_options(client, monkeypatch):
    call_command('seed_sample_data')
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    backing_locations = location_repository.find_all()
    initial_location_codes = [location.unlocode.value for location in backing_locations]
    monkeypatch.setattr(location_repository, 'find_all', lambda: backing_locations)
    url = f'/admin/cargo/{cargo.tracking_id.value}/destination/'

    first = client.get(url)
    second = client.get(url)
    content = first.content.decode()
    options = re.search(r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', content, re.DOTALL)
    repeated_options = re.search(
        r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>',
        second.content.decode(),
        re.DOTALL,
    )

    assert first.status_code == 200
    assert '<dialog' in content and 'Change destination' in content
    assert f'action="{url}" hx-post="{url}"' in content
    assert 'destination-error' not in content
    assert cargo.route_specification.origin.name in content
    assert cargo.route_specification.destination.name in content
    assert options is not None and repeated_options is not None
    assert options.group(1) == repeated_options.group(1)
    option_values = re.findall(r'<option value="([^"]*)"', options.group(1))
    expected_values = {
        '',
        *(
            location.unlocode.value
            for location in backing_locations
            if location
            not in (cargo.route_specification.origin, cargo.route_specification.destination)
        ),
    }
    assert set(option_values) == expected_values
    assert cargo.route_specification.origin.unlocode.value not in options.group(1)
    assert cargo.route_specification.destination.unlocode.value not in options.group(1)
    assert [location.unlocode.value for location in backing_locations] == initial_location_codes


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_shows_initial_value_and_parse_error_near_the_field(client):
    call_command('seed_sample_data')
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    url = f'/admin/cargo/{cargo.tracking_id.value}/deadline/'

    initial = client.get(url)
    initial_content = initial.content.decode()
    assert f'value="{cargo.route_specification.arrival_deadline:%Y-%m-%d}"' in initial_content
    assert f'action="{url}" hx-post="{url}"' in initial_content
    assert cargo.route_specification.origin.name in initial_content
    assert cargo.route_specification.destination.name in initial_content
    assert 'deadline-error' not in initial_content

    invalid = client.post(
        url,
        {'arrival_deadline': '2031-02-31'},
        HTTP_HX_REQUEST='true',
    )
    content = invalid.content.decode()

    assert invalid.status_code == 200
    assert (
        '<p id="deadline-error" class="mt-2 text-red-700" role="alert">'
        'Enter a valid arrival deadline.</p>'
    ) in content
    assert 'aria-invalid="true"' in content
    assert 'value="2031-02-31"' in content
    assert cargo_repository.find(cargo.tracking_id).route_specification == cargo.route_specification

    missing_value = client.post(url, {}, HTTP_HX_REQUEST='true')
    missing_content = missing_value.content.decode()
    assert missing_value.status_code == 200
    assert 'Enter a valid arrival deadline.' in missing_content
    assert 'value=""' in missing_content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_rejects_a_filtered_out_destination(client):
    call_command('seed_sample_data')
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    url = f'/admin/cargo/{cargo.tracking_id.value}/destination/'

    response = client.post(
        url,
        {'destination': cargo.route_specification.origin.unlocode.value},
        HTTP_HX_REQUEST='true',
    )
    content = response.content.decode()

    assert response.status_code == 200
    assert (
        '<p id="destination-error" class="mt-2 text-red-700" role="alert">'
        'Select a valid destination.</p>'
    ) in content
    assert cargo_repository.find(cargo.tracking_id).route_specification == cargo.route_specification


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_updates_through_specification_and_refreshes(client):
    call_command('seed_sample_data')
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    destination = next(
        location
        for location in location_repository.find_all()
        if location not in (cargo.route_specification.origin, cargo.route_specification.destination)
    )
    url = f'/admin/cargo/{cargo.tracking_id.value}/destination/'

    response = client.post(
        url,
        {'destination': destination.unlocode.value},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 204
    assert response.headers['HX-Refresh'] == 'true'
    updated = cargo_repository.find(cargo.tracking_id)
    assert updated is not None
    assert updated.route_specification.origin == cargo.route_specification.origin
    assert updated.route_specification.destination == destination
    assert (
        updated.route_specification.arrival_deadline == cargo.route_specification.arrival_deadline
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_updates_through_specification_and_refreshes(client):
    call_command('seed_sample_data')
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    deadline = datetime(2031, 2, 3, tzinfo=UTC)
    url = f'/admin/cargo/{cargo.tracking_id.value}/deadline/'

    response = client.post(
        url,
        {'arrival_deadline': '2031-02-03'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 204
    assert response.headers['HX-Refresh'] == 'true'
    updated = cargo_repository.find(cargo.tracking_id)
    assert updated is not None
    assert updated.route_specification.origin == cargo.route_specification.origin
    assert updated.route_specification.destination == cargo.route_specification.destination
    assert updated.route_specification.arrival_deadline == deadline


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
@pytest.mark.parametrize(
    'url',
    (
        '/admin/cargo/DEF789/destination/',
        '/admin/cargo/DEF789/deadline/',
    ),
)
def test_dialog_views_reject_unsupported_methods(client, url):
    call_command('seed_sample_data')

    assert client.put(url).status_code == 405


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('view', 'url'),
    (
        (destination_dialog_view, '/admin/cargo/MISSING1/destination/'),
        (deadline_dialog_view, '/admin/cargo/MISSING1/deadline/'),
    ),
)
def test_dialog_views_report_missing_cargo(view, url):
    with pytest.raises(Http404, match='Cargo with tracking ID MISSING1 not found\\.'):
        view(RequestFactory().get(url), 'MISSING1')
