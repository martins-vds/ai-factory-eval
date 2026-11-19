import re
from datetime import UTC, datetime

import pytest
from django.core.management import call_command
from django.test import override_settings
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
shipping_locations = []


def list_shipping_locations():
    return shipping_locations


cargo_dashboard = CargoDashboard(cargo_repository)
destination_dialog, deadline_dialog = create_dialog_views(
    CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
    cargo_dashboard,
    list_shipping_locations,
)
dashboard, _ = create_booking_views(cargo_dashboard)
urlpatterns = [
    path('admin/dashboard/', dashboard),
    path('admin/cargo/<str:tracking_id>/destination/', destination_dialog),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_dialog),
]


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_shows_values_and_filters_options_without_mutating_locations(client):
    call_command('seed_sample_data')
    shipping_locations[:] = location_repository.find_all()
    original_codes = [location.unlocode.value for location in shipping_locations]

    response = client.get('/admin/cargo/DEF789/destination/')
    second_response = client.get('/admin/cargo/DEF789/destination/')
    content = response.content.decode()
    options = re.search(r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', content, re.DOTALL)
    second_options = re.search(
        r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>',
        second_response.content.decode(),
        re.DOTALL,
    )

    assert response.status_code == 200
    assert 'Hong Kong' in content and 'Melbourne' in content
    assert options is not None
    assert 'value="CNHKG"' not in options.group(1)
    assert 'value="AUMEL"' not in options.group(1)
    assert 'value="SEGOT" selected' in options.group(1)
    assert [location.unlocode.value for location in shipping_locations] == original_codes
    assert second_options is not None
    assert second_options.group(1) == options.group(1)


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_shows_current_route_specification_values(client):
    call_command('seed_sample_data')
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None

    response = client.get('/admin/cargo/DEF789/deadline/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Hong Kong' in content and 'Melbourne' in content
    assert f'value="{cargo.route_specification.arrival_deadline.date().isoformat()}"' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_reports_unparseable_value_without_changing_cargo(client):
    call_command('seed_sample_data')
    before = cargo_repository.find(TrackingId('DEF789'))
    assert before is not None

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': 'not-a-date'},
        HTTP_HX_REQUEST='true',
    )
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Enter a valid arrival deadline.' in content
    assert 'aria-invalid="true"' in content
    assert 'value="not-a-date"' in content
    assert (
        cargo_repository.find(TrackingId('DEF789')).route_specification
        == before.route_specification
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_update_preserves_other_specification_fields_and_completes_dialog(client):
    call_command('seed_sample_data')
    before = cargo_repository.find(TrackingId('DEF789'))
    assert before is not None

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'USNYC'},
        HTTP_HX_REQUEST='true',
    )
    content = response.content.decode()
    updated = cargo_repository.find(TrackingId('DEF789'))
    assert updated is not None

    assert response.status_code == 200
    assert response['HX-Retarget'] == '#not-routed-cargo'
    assert response['HX-Reswap'] == 'outerHTML'
    assert 'New York' in content
    assert '<dialog' not in content
    assert 'Widget for var' not in content
    assert updated.route_specification.origin == before.route_specification.origin
    assert updated.route_specification.destination.unlocode.value == 'USNYC'
    assert (
        updated.route_specification.arrival_deadline == before.route_specification.arrival_deadline
    )
    assert 'data-tracking-id="DEF789"' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_update_preserves_other_specification_fields_and_refreshes_table(client):
    call_command('seed_sample_data')
    before = cargo_repository.find(TrackingId('DEF789'))
    assert before is not None

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': '2027-01-15'},
        HTTP_HX_REQUEST='true',
    )
    content = response.content.decode()
    updated = cargo_repository.find(TrackingId('DEF789'))
    assert updated is not None

    assert response.status_code == 200
    assert '01/15/2027' in content
    assert '<dialog' not in content
    assert 'Widget for var' not in content
    assert updated.route_specification.origin == before.route_specification.origin
    assert updated.route_specification.destination == before.route_specification.destination
    assert updated.route_specification.arrival_deadline == datetime(2027, 1, 15, tzinfo=UTC)
    assert 'data-tracking-id="DEF789"' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_not_routed_table_opens_destination_and_deadline_dialogs(client):
    call_command('seed_sample_data')

    response = client.get('/admin/dashboard/')
    table = response.content.decode().split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]

    assert response.status_code == 200
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in table
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in table


@pytest.mark.parametrize('dialog', ('destination', 'deadline'))
@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_unknown_cargo_returns_not_found_from_both_dialogs(client, dialog):
    response = client.get(f'/admin/cargo/MISSING1/{dialog}/')

    assert response.status_code == 404
