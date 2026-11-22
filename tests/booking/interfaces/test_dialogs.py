import re

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.booking.interfaces.dialogs.views import create_booking_dialog_views
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.models import CargoRecord
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository

cargo_repository = DjangoCargoRepository()
location_repository = DjangoLocationRepository()
shipping_locations = []


def _shipping_locations():
    return shipping_locations


dashboard_view, _ = create_booking_views(CargoDashboard(cargo_repository))
destination_dialog_view, deadline_dialog_view = create_booking_dialog_views(
    CargoDashboard(cargo_repository),
    CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
    _shipping_locations,
)
urlpatterns = [
    path('admin/dashboard/', dashboard_view),
    path('admin/cargo/<str:tracking_id>/destination/', destination_dialog_view),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_dialog_view),
]


def _seed_booking_data():
    call_command('seed_sample_data')
    shipping_locations[:] = location_repository.find_all()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_not_routed_table_opens_destination_and_deadline_dialogs(client):
    _seed_booking_data()

    response = client.get('/admin/dashboard/')
    content = response.content.decode()
    not_routed_table = content.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]

    assert response.status_code == 200
    assert 'href="/admin/cargo/DEF789/route/"' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in not_routed_table
    assert 'Change destination for cargo DEF789' in not_routed_table
    assert 'Change arrival deadline for cargo DEF789' in not_routed_table


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_shows_current_values_and_stable_filtered_options(client):
    _seed_booking_data()
    original_locations = tuple(shipping_locations)
    url = '/admin/cargo/DEF789/destination/'

    first_response = client.get(url, HTTP_HX_REQUEST='true')
    second_response = client.get(url, HTTP_HX_REQUEST='true')
    content = first_response.content.decode()
    options = re.search(r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', content, re.DOTALL)

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert 'Hong Kong' in content
    assert 'Melbourne' in content
    assert options is not None
    assert 'value="CNHKG"' not in options.group(1)
    assert 'value="AUMEL"' not in options.group(1)
    assert options.group(1).count('<option') == len(original_locations) - 2
    assert tuple(shipping_locations) == original_locations
    assert second_response.content == first_response.content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_update_preserves_other_specification_fields_and_refreshes_table(client):
    _seed_booking_data()
    before = cargo_repository.find(TrackingId('DEF789'))
    assert before is not None

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'USNYC'},
        HTTP_HX_REQUEST='true',
    )
    updated = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 200
    assert response.headers['HX-Retarget'] == '#not-routed-cargo'
    assert 'id="not-routed-cargo"' in response.content.decode()
    assert 'New York' in response.content.decode()
    assert 'Widget for var' not in response.content.decode()
    assert updated is not None
    assert updated.route_specification.origin == before.route_specification.origin
    assert updated.route_specification.destination.unlocode.value == 'USNYC'
    assert updated.route_specification.arrival_deadline == before.route_specification.arrival_deadline


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_shows_initial_value_and_parse_error_without_updating_cargo(client):
    _seed_booking_data()
    before = cargo_repository.find(TrackingId('DEF789'))
    assert before is not None

    initial_response = client.get('/admin/cargo/DEF789/deadline/', HTTP_HX_REQUEST='true')
    invalid_response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': 'not-a-date'},
        HTTP_HX_REQUEST='true',
    )
    after = cargo_repository.find(TrackingId('DEF789'))

    assert initial_response.status_code == 200
    assert 'name="deadline"' in initial_response.content.decode()
    assert 'value="' + before.route_specification.arrival_deadline.strftime('%Y-%m-%d') + '"' in (
        initial_response.content.decode()
    )
    assert invalid_response.status_code == 200
    assert 'Enter a valid arrival deadline.' in invalid_response.content.decode()
    assert 'aria-invalid="true"' in invalid_response.content.decode()
    assert after is not None
    assert after.route_specification == before.route_specification


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_update_preserves_other_specification_fields_and_refreshes_table(client):
    _seed_booking_data()
    before = cargo_repository.find(TrackingId('DEF789'))
    assert before is not None

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': '2027-01-15'},
        HTTP_HX_REQUEST='true',
    )
    updated = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 200
    assert response.headers['HX-Retarget'] == '#not-routed-cargo'
    assert '01/15/2027' in response.content.decode()
    assert 'Widget for var' not in response.content.decode()
    assert updated is not None
    assert updated.route_specification.origin == before.route_specification.origin
    assert updated.route_specification.destination == before.route_specification.destination
    assert updated.route_specification.arrival_deadline.strftime('%Y-%m-%d') == '2027-01-15'
