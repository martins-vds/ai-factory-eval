import re
from datetime import date

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.booking.interfaces.dialogs.views import create_booking_dialog_views
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository

available_locations = []
cargo_repository = DjangoCargoRepository()
location_repository = DjangoLocationRepository()
dashboard_view, _ = create_booking_views(CargoDashboard(cargo_repository))
destination_dialog_view, deadline_dialog_view = create_booking_dialog_views(
    CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
    CargoDashboard(cargo_repository),
    lambda: available_locations,
)
urlpatterns = [
    path('admin/dashboard/', dashboard_view),
    path('admin/cargo/<str:tracking_id>/destination/', destination_dialog_view),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_dialog_view),
]


@pytest.fixture(autouse=True)
def reset_locations():
    available_locations.clear()


def _seed_booking_data():
    call_command('seed_sample_data')
    available_locations.extend(location_repository.find_all())


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_not_routed_table_opens_dialogs_and_refreshes_after_dialog_completion(client):
    _seed_booking_data()

    response = client.get('/admin/dashboard/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in content
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in content
    assert 'id="booking-dialog-content"' in content
    assert 'hx-trigger="bookingCargoUpdated from:body"' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_shows_current_values_and_stable_filtered_options(client):
    _seed_booking_data()

    first_response = client.get('/admin/cargo/DEF789/destination/')
    first_content = first_response.content.decode()
    initial_location_list = available_locations.copy()
    first_options = re.search(
        r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', first_content, re.DOTALL
    )
    second_content = client.get('/admin/cargo/DEF789/destination/').content.decode()
    second_options = re.search(
        r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', second_content, re.DOTALL
    )

    assert first_response.status_code == 200
    assert 'Hong Kong' in first_content and 'Melbourne' in first_content
    assert first_options is not None and second_options is not None
    assert 'CNHKG' not in first_options.group(1)
    assert 'AUMEL' not in first_options.group(1)
    assert first_options.group(1) == second_options.group(1)
    assert available_locations == initial_location_list


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_reports_invalid_dates_without_losing_current_fields(client):
    _seed_booking_data()

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': 'not-a-date'},
    )
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Enter a valid arrival deadline.' in content
    assert 'aria-invalid="true"' in content
    assert 'Hong Kong' in content
    assert 'Melbourne' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_successful_destination_change_completes_dialog_and_refreshes_table(client):
    _seed_booking_data()
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    original_origin = cargo.route_specification.origin
    original_deadline = cargo.route_specification.arrival_deadline

    response = client.post(
        f'/admin/cargo/{cargo.tracking_id.value}/destination/',
        {'destination': 'USNYC'},
    )

    updated_cargo = cargo_repository.find(cargo.tracking_id)
    dashboard = client.get('/admin/dashboard/').content.decode()

    assert response.status_code == 204
    assert response['HX-Trigger'] == 'bookingDialogClose, bookingCargoUpdated'
    assert updated_cargo is not None
    assert updated_cargo.route_specification.origin == original_origin
    assert updated_cargo.route_specification.destination.unlocode.value == 'USNYC'
    assert updated_cargo.route_specification.arrival_deadline == original_deadline
    assert 'New York' in dashboard
    assert 'USNYC' in dashboard


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_successful_deadline_change_completes_dialog_and_refreshes_table(client):
    _seed_booking_data()
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    original_origin = cargo.route_specification.origin
    original_destination = cargo.route_specification.destination

    response = client.post(
        f'/admin/cargo/{cargo.tracking_id.value}/deadline/',
        {'deadline': '2035-02-14'},
    )

    updated_cargo = cargo_repository.find(cargo.tracking_id)
    dashboard = client.get('/admin/dashboard/').content.decode()

    assert response.status_code == 204
    assert response['HX-Trigger'] == 'bookingDialogClose, bookingCargoUpdated'
    assert updated_cargo is not None
    assert updated_cargo.route_specification.arrival_deadline.date() == date(2035, 2, 14)
    assert updated_cargo.route_specification.origin == original_origin
    assert updated_cargo.route_specification.destination == original_destination
    assert '02/14/2035' in dashboard


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_dialog_forms_include_cancel_and_invalid_destinations_do_not_update(client):
    _seed_booking_data()
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    original_destination = cargo.route_specification.destination

    dialog = client.get(f'/admin/cargo/{cargo.tracking_id.value}/destination/').content.decode()
    response = client.post(
        f'/admin/cargo/{cargo.tracking_id.value}/destination/',
        {'destination': 'CNHKG'},
    )

    updated_cargo = cargo_repository.find(cargo.tracking_id)

    assert 'formmethod="dialog"' in dialog
    assert 'Cancel' in dialog
    assert 'Select a valid destination.' in response.content.decode()
    assert updated_cargo is not None
    assert updated_cargo.route_specification.destination == original_destination
