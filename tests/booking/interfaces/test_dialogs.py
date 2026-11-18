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

cargo_repository = DjangoCargoRepository()
location_repository = DjangoLocationRepository()
dashboard = CargoDashboard(cargo_repository)
specification = CargoSpecification(cargo_repository, DjangoHandlingEventRepository())
destination_view = create_destination_dialog_view(
    dashboard, specification, location_repository.find_all
)
deadline_view = create_deadline_dialog_view(dashboard, specification)
dashboard_view, _ = create_booking_views(dashboard)
urlpatterns = [
    path('admin/cargo/<str:tracking_id>/destination/', destination_view),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_view),
    path('admin/dashboard/', dashboard_view),
]


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_filters_options_without_mutating_locations(client):
    call_command('seed_sample_data')
    locations_before = location_repository.find_all()

    response = client.get('/admin/cargo/DEF789/destination/')
    second_response = client.get('/admin/cargo/DEF789/destination/')

    assert response.status_code == 200
    content = response.content.decode()
    select = re.search(r'<select\b.*?</select>', content, re.DOTALL).group()
    option_codes = re.findall(r'<option value="([^"]+)"', select)
    second_select = re.search(
        r'<select\b.*?</select>', second_response.content.decode(), re.DOTALL
    ).group()
    second_option_codes = re.findall(r'<option value="([^"]+)"', second_select)

    assert 'Hong Kong' in content
    assert 'Melbourne' in content
    assert 'CNHKG' not in option_codes
    assert 'AUMEL' not in option_codes
    assert locations_before == location_repository.find_all()
    assert option_codes == second_option_codes


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_shows_current_route_and_deadline(client):
    call_command('seed_sample_data')

    response = client.get('/admin/cargo/DEF789/deadline/')
    cargo = dashboard.get_cargo_details(TrackingId('DEF789'))

    assert response.status_code == 200
    content = response.content.decode()
    assert cargo is not None
    assert cargo.route_specification.origin.name in content
    assert cargo.route_specification.destination.name in content
    assert f'value="{cargo.route_specification.arrival_deadline.date().isoformat()}"' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_invalid_deadline_renders_field_error_without_updating_cargo(client):
    call_command('seed_sample_data')
    original_deadline = dashboard.get_cargo_details(TrackingId('DEF789')).route_specification.arrival_deadline

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': 'not-a-date'},
        HTTP_HX_REQUEST='true',
    )
    updated_cargo = dashboard.get_cargo_details(TrackingId('DEF789'))

    assert response.status_code == 200
    assert 'Enter a valid arrival deadline.' in response.content.decode()
    assert 'aria-invalid="true"' in response.content.decode()
    assert updated_cargo.route_specification.arrival_deadline == original_deadline


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_update_refreshes_not_routed_table_and_preserves_route(client):
    call_command('seed_sample_data')
    original_cargo = dashboard.get_cargo_details(TrackingId('DEF789'))
    new_deadline = '2027-01-15'

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': new_deadline},
        HTTP_HX_REQUEST='true',
    )
    updated_cargo = dashboard.get_cargo_details(TrackingId('DEF789'))

    assert response.status_code == 200
    assert response.headers['HX-Retarget'] == '#not-routed-cargo'
    assert response.headers['HX-Reswap'] == 'outerHTML'
    assert '01/15/2027' in response.content.decode()
    assert 'DEF789' in response.content.decode()
    assert 'Widget for var' not in response.content.decode()
    assert original_cargo is not None
    assert updated_cargo is not None
    assert updated_cargo.route_specification.origin == original_cargo.route_specification.origin
    assert (
        updated_cargo.route_specification.destination
        == original_cargo.route_specification.destination
    )
    assert updated_cargo.route_specification.arrival_deadline.date().isoformat() == new_deadline


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_update_refreshes_table_and_preserves_other_specification_fields(client):
    call_command('seed_sample_data')
    original_cargo = dashboard.get_cargo_details(TrackingId('DEF789'))

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'USNYC'},
        HTTP_HX_REQUEST='true',
    )
    updated_cargo = dashboard.get_cargo_details(TrackingId('DEF789'))

    assert response.status_code == 200
    assert response.headers['HX-Retarget'] == '#not-routed-cargo'
    assert 'New York' in response.content.decode()
    assert 'DEF789' in response.content.decode()
    assert 'Widget for var' not in response.content.decode()
    assert original_cargo is not None
    assert updated_cargo is not None
    assert updated_cargo.route_specification.origin == original_cargo.route_specification.origin
    assert (
        updated_cargo.route_specification.arrival_deadline
        == original_cargo.route_specification.arrival_deadline
    )
    assert updated_cargo.route_specification.destination.unlocode.value == 'USNYC'


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_not_routed_table_opens_edit_dialogs_without_changing_route_link(client):
    call_command('seed_sample_data')

    response = client.get('/admin/dashboard/')
    not_routed_table = response.content.decode().split('id="not-routed-cargo"', 1)[1].split(
        '</section>', 1
    )[0]

    assert response.status_code == 200
    assert 'href="/admin/cargo/DEF789/route/"' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in not_routed_table
    assert 'aria-label="Change destination for cargo DEF789"' in not_routed_table
    assert 'aria-label="Change deadline for cargo DEF789"' in not_routed_table
    assert 'id="cargo-edit-dialog"' in not_routed_table
