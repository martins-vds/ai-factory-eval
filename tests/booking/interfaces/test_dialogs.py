import re
from datetime import date

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.booking.interfaces.dialogs.views import create_booking_dialog_views
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository

cargo_repository = DjangoCargoRepository()
location_repository = DjangoLocationRepository()
available_locations = []
destination_dialog_view, deadline_dialog_view = create_booking_dialog_views(
    CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
    CargoDashboard(cargo_repository),
    lambda: available_locations,
)
urlpatterns = [
    path('admin/cargo/<str:tracking_id>/destination/', destination_dialog_view),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_dialog_view),
]


@pytest.fixture
def not_routed_cargo():
    call_command('seed_sample_data')
    available_locations[:] = location_repository.find_all()
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    return cargo


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_shows_current_values_and_stable_filtered_options(
    client, not_routed_cargo
):
    original_locations = tuple(available_locations)

    first_response = client.get('/admin/cargo/DEF789/destination/')
    second_response = client.get('/admin/cargo/DEF789/destination/')
    first_content = first_response.content.decode()
    second_content = second_response.content.decode()

    first_options = re.search(r'<select\b[^>]*id="destination"[^>]*>(.*?)</select>', first_content)
    second_options = re.search(
        r'<select\b[^>]*id="destination"[^>]*>(.*?)</select>', second_content
    )
    assert first_response.status_code == 200
    assert not_routed_cargo.route_specification.origin.name in first_content
    assert not_routed_cargo.route_specification.destination.name in first_content
    assert first_options is not None and second_options is not None
    assert first_options.group(1) == second_options.group(1)
    assert not_routed_cargo.route_specification.origin.unlocode.value not in first_options.group(1)
    assert (
        not_routed_cargo.route_specification.destination.unlocode.value
        not in first_options.group(1)
    )
    assert 'USNYC' in first_options.group(1)
    assert tuple(available_locations) == original_locations


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_shows_current_values(client, not_routed_cargo):
    response = client.get('/admin/cargo/DEF789/deadline/')
    content = response.content.decode()

    assert response.status_code == 200
    assert not_routed_cargo.route_specification.origin.name in content
    assert not_routed_cargo.route_specification.destination.name in content
    assert (
        f'value="{not_routed_cargo.route_specification.arrival_deadline.date().isoformat()}"'
        in content
    )
    assert 'Cancel' in content
    assert 'Update' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_unparseable_deadline_shows_inline_field_error_without_updating(
    client, not_routed_cargo
):
    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': 'not-a-date'},
        HTTP_HX_REQUEST='true',
    )
    reloaded_cargo = cargo_repository.find(not_routed_cargo.tracking_id)
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Enter a valid arrival deadline.' in content
    assert 'aria-describedby="deadline-error"' in content
    assert 'aria-invalid="true"' in content
    assert reloaded_cargo.route_specification.arrival_deadline == (
        not_routed_cargo.route_specification.arrival_deadline
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_update_preserves_other_specification_fields_and_refreshes_rows(
    client, not_routed_cargo
):
    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'USNYC'},
        HTTP_HX_REQUEST='true',
    )
    updated_cargo = cargo_repository.find(not_routed_cargo.tracking_id)
    content = response.content.decode()

    assert response.status_code == 200
    assert updated_cargo.route_specification.destination.unlocode.value == 'USNYC'
    assert updated_cargo.route_specification.origin == not_routed_cargo.route_specification.origin
    assert (
        updated_cargo.route_specification.arrival_deadline
        == not_routed_cargo.route_specification.arrival_deadline
    )
    assert 'New York' in content
    assert response.headers['HX-Retarget'] == '#not-routed-cargo'
    assert response.headers['HX-Reswap'] == 'outerHTML'
    assert 'Widget for var' not in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_update_preserves_other_specification_fields_and_refreshes_rows(
    client, not_routed_cargo
):
    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': '2027-01-03'},
        HTTP_HX_REQUEST='true',
    )
    updated_cargo = cargo_repository.find(not_routed_cargo.tracking_id)
    content = response.content.decode()

    assert response.status_code == 200
    assert updated_cargo.route_specification.arrival_deadline.date() == date(2027, 1, 3)
    assert updated_cargo.route_specification.origin == not_routed_cargo.route_specification.origin
    assert (
        updated_cargo.route_specification.destination
        == not_routed_cargo.route_specification.destination
    )
    assert '01/03/2027' in content
    assert response.headers['HX-Retarget'] == '#not-routed-cargo'
    assert response.headers['HX-Reswap'] == 'outerHTML'
    assert 'Widget for var' not in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_missing_cargo_error_is_renderable_in_the_dialog(client, not_routed_cargo):
    response = client.get('/admin/cargo/UNKNOWN/destination/')

    assert response.status_code == 404
    assert 'Cargo not found' in response.content.decode()
