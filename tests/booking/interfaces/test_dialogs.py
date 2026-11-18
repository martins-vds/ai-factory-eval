import re
from datetime import date

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

cargo_repository = DjangoCargoRepository()
location_repository = DjangoLocationRepository()
dashboard = CargoDashboard(cargo_repository)
destination_dialog_view = create_destination_dialog_view(
    dashboard,
    CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
    location_repository.find_all,
)
deadline_dialog_view = create_deadline_dialog_view(
    dashboard,
    CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
)
dashboard_view, _ = create_booking_views(dashboard)
urlpatterns = [
    path('admin/dashboard/', dashboard_view),
    path('admin/cargo/<str:tracking_id>/destination/', destination_dialog_view),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_dialog_view),
]


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_shows_current_route_specification_and_filtered_options(client):
    call_command('seed_sample_data')

    response = client.get('/admin/cargo/DEF789/destination/')
    content = response.content.decode()
    options = re.search(r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', content, re.DOTALL)

    assert response.status_code == 200
    assert 'Change destination' in content
    assert 'Hong Kong' in content
    assert 'Melbourne' in content
    assert response.context['destination_error'] == ''
    assert options is not None
    assert 'USNYC' in options.group(1)
    assert 'CNHKG' not in options.group(1)
    assert 'AUMEL' not in options.group(1)


@pytest.mark.django_db
def test_destination_options_are_stable_across_renders():
    call_command('seed_sample_data')
    backing_locations = location_repository.find_all()
    view = create_destination_dialog_view(
        dashboard,
        CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
        lambda: backing_locations,
    )
    original_codes = tuple(location.unlocode.value for location in backing_locations)
    factory = RequestFactory()

    first_content = view(factory.get('/'), 'DEF789').content.decode()
    second_content = view(factory.get('/'), 'DEF789').content.decode()
    first_options = re.search(
        r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', first_content, re.DOTALL
    )
    second_options = re.search(
        r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', second_content, re.DOTALL
    )

    assert first_options is not None
    assert second_options is not None
    assert first_options.group(1) == second_options.group(1)
    assert tuple(location.unlocode.value for location in backing_locations) == original_codes


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_not_routed_table_opens_destination_and_deadline_dialogs(client):
    call_command('seed_sample_data')

    response = client.get('/admin/dashboard/')
    not_routed_table = (
        response.content.decode().split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]
    )

    assert response.status_code == 200
    assert 'Change destination' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in not_routed_table
    assert 'Change arrival deadline' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in not_routed_table
    assert 'id="cargo-dialog"' in response.content.decode()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_not_routed_table_swaps_dialog_error_responses(client):
    call_command('seed_sample_data')

    response = client.get('/admin/dashboard/')

    assert response.status_code == 200
    assert (
        'hx-on::before-swap="if (event.detail.xhr.status >= 400) event.detail.shouldSwap = true"'
    ) in response.content.decode()


@pytest.mark.django_db
@pytest.mark.parametrize('dialog', ['destination', 'deadline'])
@override_settings(ROOT_URLCONF=__name__)
def test_dialog_returns_not_found_for_unknown_cargo(client, dialog):
    call_command('seed_sample_data')

    response = client.get(f'/admin/cargo/UNKNOWN/{dialog}/')

    assert response.status_code == 404
    assert 'UNKNOWN' in response.content.decode()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_rejects_origin_without_changing_route(client):
    call_command('seed_sample_data')

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'CNHKG'},
        HTTP_HX_REQUEST='true',
    )
    cargo = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 200
    assert response.context['destination_error'] == 'Select a valid destination.'
    assert 'Select a valid destination.' in response.content.decode()
    assert 'aria-invalid="true"' in response.content.decode()
    assert cargo is not None
    assert cargo.route_specification.destination.unlocode.value == 'AUMEL'


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_updates_destination_preserves_route_and_refreshes_table(client):
    call_command('seed_sample_data')
    cargo = dashboard.get_cargo_details(TrackingId('DEF789'))
    assert cargo is not None
    original_origin = cargo.route_specification.origin
    original_deadline = cargo.route_specification.arrival_deadline

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'USNYC'},
        HTTP_HX_REQUEST='true',
    )
    updated_cargo = cargo_repository.find(TrackingId('DEF789'))
    refreshed_dashboard = client.get('/admin/dashboard/')
    not_routed_table = (
        refreshed_dashboard.content.decode()
        .split('id="not-routed-cargo"', 1)[1]
        .split('</section>', 1)[0]
    )

    assert response.status_code == 200
    assert response.content == b''
    assert response.headers['HX-Trigger'] == 'cargo-updated'
    assert b'Widget for var' not in response.content
    assert updated_cargo is not None
    assert updated_cargo.route_specification.origin == original_origin
    assert updated_cargo.route_specification.destination.unlocode.value == 'USNYC'
    assert updated_cargo.route_specification.arrival_deadline == original_deadline
    assert 'New York' in not_routed_table
    assert 'USNYC' in not_routed_table


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_redirects_after_non_htmx_update(client):
    call_command('seed_sample_data')

    response = client.post('/admin/cargo/DEF789/destination/', {'destination': 'USNYC'})

    assert response.status_code == 302
    assert response.headers['Location'] == '/admin/dashboard/'


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_shows_current_route_specification_and_deadline(client):
    call_command('seed_sample_data')
    cargo = dashboard.get_cargo_details(TrackingId('DEF789'))
    assert cargo is not None

    response = client.get('/admin/cargo/DEF789/deadline/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Change arrival deadline' in content
    assert 'Hong Kong' in content
    assert 'Melbourne' in content
    assert response.context['deadline_error'] == ''
    assert f'min="{response.context["today"].isoformat()}"' in content
    assert f'value="{cargo.route_specification.arrival_deadline.date().isoformat()}"' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_shows_parse_error_without_changing_deadline(client):
    call_command('seed_sample_data')
    cargo = dashboard.get_cargo_details(TrackingId('DEF789'))
    assert cargo is not None
    original_deadline = cargo.route_specification.arrival_deadline

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': 'not-a-date'},
        HTTP_HX_REQUEST='true',
    )
    content = response.content.decode()
    updated_cargo = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 200
    assert response.context['deadline_error'] == 'Enter a valid arrival deadline.'
    assert 'Enter a valid arrival deadline.' in content
    assert 'aria-invalid="true"' in content
    assert updated_cargo is not None
    assert updated_cargo.route_specification.arrival_deadline == original_deadline


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_keeps_an_empty_value_when_deadline_is_missing(client):
    call_command('seed_sample_data')

    response = client.post('/admin/cargo/DEF789/deadline/', {}, HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert response.context['deadline_value'] == ''
    assert response.context['deadline_error'] == 'Enter a valid arrival deadline.'


@pytest.mark.django_db
def test_deadline_update_use_case_rejects_an_unparsed_value():
    call_command('seed_sample_data')
    specification = CargoSpecification(cargo_repository, DjangoHandlingEventRepository())

    with pytest.raises(TypeError, match='Arrival deadline must be a datetime'):
        specification.change_deadline(TrackingId('DEF789'), 'not-a-date')


@pytest.mark.django_db
def test_destination_update_use_case_rejects_origin_as_destination():
    call_command('seed_sample_data')
    cargo = dashboard.get_cargo_details(TrackingId('DEF789'))
    assert cargo is not None
    specification = CargoSpecification(cargo_repository, DjangoHandlingEventRepository())

    with pytest.raises(ValueError, match="Origin and destination can't be the same"):
        specification.change_destination(
            cargo.tracking_id,
            cargo.route_specification.origin,
        )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_updates_deadline_preserves_route_and_refreshes_table(client):
    call_command('seed_sample_data')
    cargo = dashboard.get_cargo_details(TrackingId('DEF789'))
    assert cargo is not None
    expected_deadline = date(2030, 11, 20)
    original_origin = cargo.route_specification.origin
    original_destination = cargo.route_specification.destination

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': expected_deadline.isoformat()},
        HTTP_HX_REQUEST='true',
    )
    updated_cargo = cargo_repository.find(TrackingId('DEF789'))
    refreshed_dashboard = client.get('/admin/dashboard/')
    not_routed_table = (
        refreshed_dashboard.content.decode()
        .split('id="not-routed-cargo"', 1)[1]
        .split('</section>', 1)[0]
    )

    assert response.status_code == 200
    assert response.content == b''
    assert response.headers['HX-Trigger'] == 'cargo-updated'
    assert b'Widget for var' not in response.content
    assert updated_cargo is not None
    assert updated_cargo.route_specification.arrival_deadline.date() == expected_deadline
    assert updated_cargo.route_specification.origin == original_origin
    assert updated_cargo.route_specification.destination == original_destination
    assert '11/20/2030' in not_routed_table
