from datetime import datetime

import pytest
from django.core.management import call_command
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
dashboard = CargoDashboard(cargo_repository)
destination_dialog_view, deadline_dialog_view = create_booking_dialog_views(
    dashboard,
    CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
    location_repository.find_all,
)
dashboard_view, _ = create_booking_views(dashboard)
urlpatterns = [
    path('admin/dashboard/', dashboard_view),
    path('admin/cargo/<str:tracking_id>/destination/', destination_dialog_view),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_dialog_view),
]


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_not_routed_table_opens_destination_and_deadline_dialogs(client):
    call_command('seed_sample_data')

    dashboard_response = client.get('/admin/dashboard/')
    destination_response = client.get('/admin/cargo/DEF789/destination/')
    deadline_response = client.get('/admin/cargo/DEF789/deadline/')

    assert 'hx-get="/admin/cargo/DEF789/destination/"' in dashboard_response.content.decode()
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in dashboard_response.content.decode()
    assert 'Melbourne' in destination_response.content.decode()
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    expected_deadline = cargo.route_specification.arrival_deadline.date().isoformat()
    assert f'value="{expected_deadline}"' in deadline_response.content.decode()


@pytest.mark.django_db
def test_destination_options_exclude_origin_and_current_destination_without_mutating_locations():
    call_command('seed_sample_data')
    locations = location_repository.find_all()
    view, _ = create_booking_dialog_views(
        dashboard,
        CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
        lambda: locations,
    )
    request = RequestFactory().get('/admin/cargo/DEF789/destination/')

    first_response = view(request, 'DEF789')
    second_response = view(request, 'DEF789')
    options = first_response.content.decode().split('<select', 1)[1].split('</select>', 1)[0]
    subsequent_options = (
        second_response.content.decode().split('<select', 1)[1].split('</select>', 1)[0]
    )

    assert 'CNHKG' not in options
    assert 'AUMEL' not in options
    assert options.count('<option') == len(locations) - 2
    assert 'value="USNYC"' in options
    assert len(locations) == 13
    assert options == subsequent_options


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_update_completes_dialog_and_refreshes_table_without_losing_other_fields(
    client,
):
    call_command('seed_sample_data')
    original = cargo_repository.find(TrackingId('DEF789'))
    assert original is not None
    original_deadline = original.route_specification.arrival_deadline.strftime('%m/%d/%Y')

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'USNYC'},
        HTTP_HX_REQUEST='true',
    )
    refreshed_dashboard = client.get('/admin/dashboard/').content.decode()
    updated = cargo_repository.find(TrackingId('DEF789'))
    assert updated is not None

    assert response.status_code == 200
    assert response.headers['HX-Redirect'] == '/admin/dashboard/'
    assert b'unavailable' not in response.content.lower()
    assert updated.route_specification.origin == original.route_specification.origin
    assert (
        updated.route_specification.arrival_deadline
        == original.route_specification.arrival_deadline
    )
    assert 'Hong Kong' in refreshed_dashboard
    assert 'New York' in refreshed_dashboard
    assert original_deadline in refreshed_dashboard
    assert 'Melbourne' not in refreshed_dashboard


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_invalid_deadline_shows_field_error_and_keeps_cargo_unchanged(client):
    call_command('seed_sample_data')
    original = cargo_repository.find(TrackingId('DEF789'))
    assert original is not None

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': 'not-a-date'},
        HTTP_HX_REQUEST='true',
    )
    updated = cargo_repository.find(TrackingId('DEF789'))
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Enter a valid arrival deadline.' in content
    assert 'aria-invalid="true"' in content
    assert updated is not None
    assert (
        updated.route_specification.arrival_deadline
        == original.route_specification.arrival_deadline
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_update_completes_dialog_and_refreshes_table_without_losing_other_fields(client):
    call_command('seed_sample_data')
    original = cargo_repository.find(TrackingId('DEF789'))
    assert original is not None
    new_deadline = '2027-01-03'

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': new_deadline},
        HTTP_HX_REQUEST='true',
    )
    refreshed_dashboard = client.get('/admin/dashboard/').content.decode()
    updated = cargo_repository.find(TrackingId('DEF789'))
    assert updated is not None

    assert response.status_code == 200
    assert response.headers['HX-Redirect'] == '/admin/dashboard/'
    assert b'unavailable' not in response.content.lower()
    assert updated.route_specification.origin == original.route_specification.origin
    assert updated.route_specification.destination == original.route_specification.destination
    assert updated.route_specification.arrival_deadline == datetime.fromisoformat(
        f'{new_deadline}T00:00:00+00:00'
    )
    assert 'Hong Kong' in refreshed_dashboard
    assert 'Melbourne' in refreshed_dashboard
    assert '01/03/2027' in refreshed_dashboard
