import re
from datetime import UTC, datetime

import pytest
from django.core.management import call_command
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

repository = DjangoCargoRepository()
dashboard = CargoDashboard(repository)
dashboard_view, cargo_details_view = create_booking_views(dashboard)
locations = DjangoLocationRepository()
specification = CargoSpecification(repository, DjangoHandlingEventRepository())
destination_view = create_destination_dialog_view(dashboard, specification, locations.find_all)
deadline_view = create_deadline_dialog_view(dashboard, specification)
urlpatterns = [
    path('admin/dashboard/', dashboard_view),
    path('admin/cargo/<str:tracking_id>/', cargo_details_view),
    path('admin/cargo/<str:tracking_id>/destination/', destination_view),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_view),
]


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_not_routed_table_opens_destination_and_deadline_dialogs(client):
    call_command('seed_sample_data')

    response = client.get('/admin/dashboard/')
    not_routed_table = (
        response.content.decode().split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]
    )

    assert response.status_code == 200
    assert 'href="/admin/cargo/DEF789/route/"' in not_routed_table
    assert 'href="/admin/cargo/DEF789/destination/"' in not_routed_table
    assert 'href="/admin/cargo/DEF789/deadline/"' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in not_routed_table
    assert 'hx-target="#booking-dialog"' in not_routed_table
    assert 'aria-haspopup="dialog"' in not_routed_table
    assert 'id="booking-dialog"' in response.content.decode()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_shows_current_values_and_stable_filtered_options():
    call_command('seed_sample_data')
    cargo = repository.find(TrackingId('DEF789'))
    assert cargo is not None
    available_locations = locations.find_all()
    destination_view = create_destination_dialog_view(
        dashboard,
        specification,
        lambda: available_locations,
    )
    request_factory = RequestFactory()

    first_response = destination_view(
        request_factory.get('/admin/cargo/DEF789/destination/'),
        'DEF789',
    )
    second_response = destination_view(
        request_factory.get('/admin/cargo/DEF789/destination/'),
        'DEF789',
    )
    first_content = first_response.content.decode()
    options = re.findall(r'<option\s+value="([A-Z]{5})"', first_content)
    expected_options = [
        location.unlocode.value
        for location in available_locations
        if location not in (cargo.route_specification.origin, cargo.route_specification.destination)
    ]

    assert first_response.status_code == second_response.status_code == 200
    assert 'Hong Kong' in first_content and 'CNHKG' in first_content
    assert 'Melbourne' in first_content and 'AUMEL' in first_content
    assert options == expected_options
    assert re.findall(r'<option\s+value="([A-Z]{5})"', second_response.content.decode()) == (
        expected_options
    )
    assert locations.find_all() == available_locations


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_updates_cargo_and_refreshes_the_dashboard(client):
    call_command('seed_sample_data')
    cargo = repository.find(TrackingId('DEF789'))
    assert cargo is not None
    available_destination = next(
        location
        for location in locations.find_all()
        if location not in (cargo.route_specification.origin, cargo.route_specification.destination)
    )

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': available_destination.unlocode.value},
        HTTP_HX_REQUEST='true',
    )
    updated_cargo = repository.find(cargo.tracking_id)
    dashboard_response = client.get('/admin/dashboard/')
    not_routed_table = (
        dashboard_response.content.decode()
        .split('id="not-routed-cargo"', 1)[1]
        .split('</section>', 1)[0]
    )

    assert response.status_code == 204
    assert response['HX-Redirect'] == '/admin/dashboard/'
    assert response.content == b''
    assert updated_cargo is not None
    assert updated_cargo.route_specification.destination == available_destination
    assert (
        updated_cargo.route_specification.arrival_deadline
        == cargo.route_specification.arrival_deadline
    )
    assert available_destination.name in not_routed_table


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_rejects_locations_outside_the_filtered_options(client):
    call_command('seed_sample_data')
    cargo = repository.find(TrackingId('DEF789'))
    assert cargo is not None

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': cargo.route_specification.origin.unlocode.value},
    )
    updated_cargo = repository.find(cargo.tracking_id)
    content = response.content.decode()

    assert response.status_code == 200
    assert re.search(
        r'<p\b[^>]*role="alert"[^>]*>Select an available destination\.</p>',
        content,
    )
    assert 'role="alert"' in content
    assert 'Hong Kong' in content and 'Melbourne' in content
    assert re.search(r'<option\s+value="USNYC"', content)
    assert updated_cargo is not None
    assert updated_cargo.route_specification == cargo.route_specification


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_form_works_without_htmx(client):
    call_command('seed_sample_data')
    cargo = repository.find(TrackingId('DEF789'))
    assert cargo is not None
    available_destination = next(
        location
        for location in locations.find_all()
        if location not in (cargo.route_specification.origin, cargo.route_specification.destination)
    )

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': available_destination.unlocode.value},
    )
    updated_cargo = repository.find(cargo.tracking_id)

    assert response.status_code == 302
    assert response.url == '/admin/dashboard/'
    assert updated_cargo is not None
    assert updated_cargo.route_specification.destination == available_destination


@pytest.mark.parametrize(
    'path',
    (
        '/admin/cargo/MISSING1/destination/',
        '/admin/cargo/MISSING1/deadline/',
    ),
)
@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_dialogs_return_not_found_for_unknown_cargo(client, path):
    response = client.get(path)

    assert response.status_code == 404
    assert 'role="alert"' in response.content.decode()
    assert 'Cargo with tracking ID MISSING1 not found.' in response.content.decode()


@pytest.mark.parametrize(
    'path',
    (
        '/admin/cargo/MISSING1/destination/',
        '/admin/cargo/MISSING1/deadline/',
    ),
)
@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_dialogs_reject_unsupported_methods(client, path):
    response = client.put(path)

    assert response.status_code == 405
    assert response['Allow'] == 'GET, POST'


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_prefills_value_and_shows_parse_error(client):
    call_command('seed_sample_data')
    cargo = repository.find(TrackingId('DEF789'))
    assert cargo is not None
    deadline_value = cargo.route_specification.arrival_deadline.strftime('%Y-%m-%d')

    response = client.get('/admin/cargo/DEF789/deadline/')
    content = response.content.decode()
    assert response.status_code == 200
    assert 'Hong Kong' in content and 'CNHKG' in content
    assert 'Melbourne' in content and 'AUMEL' in content
    assert f'value="{deadline_value}"' in content
    assert 'hx-post="/admin/cargo/DEF789/deadline/"' in content
    assert 'Enter a valid arrival deadline.' not in content
    assert 'role="alert"' not in content

    invalid_response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': 'not-a-date'},
    )
    invalid_content = invalid_response.content.decode()

    assert invalid_response.status_code == 200
    assert re.search(
        r'<p\b[^>]*role="alert"[^>]*>Enter a valid arrival deadline\.</p>',
        invalid_content,
    )
    assert 'aria-invalid="true"' in invalid_content
    assert 'aria-describedby="deadline-error"' in invalid_content

    missing_response = client.post('/admin/cargo/DEF789/deadline/')
    assert 'value=""' in missing_response.content.decode()
    assert re.search(
        r'<p\b[^>]*role="alert"[^>]*>Enter a valid arrival deadline\.</p>',
        missing_response.content.decode(),
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_updates_cargo_and_refreshes_the_dashboard(client):
    call_command('seed_sample_data')
    cargo = repository.find(TrackingId('DEF789'))
    assert cargo is not None
    arrival_deadline = datetime(2030, 7, 14, tzinfo=UTC)

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': arrival_deadline.date().isoformat()},
        HTTP_HX_REQUEST='true',
    )
    updated_cargo = repository.find(cargo.tracking_id)
    dashboard_response = client.get('/admin/dashboard/')
    not_routed_table = (
        dashboard_response.content.decode()
        .split('id="not-routed-cargo"', 1)[1]
        .split('</section>', 1)[0]
    )

    assert response.status_code == 204
    assert response['HX-Redirect'] == '/admin/dashboard/'
    assert response.content == b''
    assert updated_cargo is not None
    assert updated_cargo.route_specification.arrival_deadline == arrival_deadline
    assert updated_cargo.route_specification.origin == cargo.route_specification.origin
    assert updated_cargo.route_specification.destination == cargo.route_specification.destination
    assert '07/14/2030' in not_routed_table
