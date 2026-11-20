import re
from datetime import timedelta

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.booking.interfaces.dialogs.views import create_booking_dialog_views
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository

repository = DjangoCargoRepository()
dashboard = CargoDashboard(repository)
destination_dialog_view, deadline_dialog_view = create_booking_dialog_views(
    CargoSpecification(repository, DjangoHandlingEventRepository()),
    dashboard,
    DjangoLocationRepository().find_all,
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

    response = client.get('/admin/dashboard/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Change Destination' in content
    assert 'Change Deadline' in content
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in content
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in content
    assert 'id="cargo-edit-dialog"' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_shows_current_values_and_stable_filtered_options(client):
    call_command('seed_sample_data')

    first = client.get('/admin/cargo/DEF789/destination/')
    second = client.get('/admin/cargo/DEF789/destination/')
    first_content = first.content.decode()
    second_content = second.content.decode()
    first_options = re.findall(r'<option value="([^"]+)"', first_content)
    second_options = re.findall(r'<option value="([^"]+)"', second_content)

    assert first.status_code == second.status_code == 200
    assert 'Hong Kong' in first_content
    assert 'Melbourne' in first_content
    assert first_options == second_options
    assert first_options
    assert 'CNHKG' not in first_options
    assert 'AUMEL' not in first_options


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_displays_current_deadline(client):
    call_command('seed_sample_data')
    cargo = repository.find(TrackingId('DEF789'))
    assert cargo is not None
    deadline = cargo.route_specification.arrival_deadline.date().isoformat()

    response = client.get('/admin/cargo/DEF789/deadline/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Hong Kong' in content
    assert 'Melbourne' in content
    assert 'name="deadline"' in content
    assert f'value="{deadline}"' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
@pytest.mark.parametrize('destination', ('CNHKG', 'AUMEL', 'UNKNOWN'))
def test_destination_dialog_rejects_unavailable_destinations(client, destination):
    call_command('seed_sample_data')
    original = repository.find(TrackingId('DEF789'))
    assert original is not None

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': destination},
        HTTP_HX_REQUEST='true',
    )
    updated = repository.find(TrackingId('DEF789'))
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Choose an available destination.' in content
    assert 'aria-invalid="true"' in content
    assert updated is not None
    assert updated.route_specification == original.route_specification


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_shows_parse_error_and_preserves_input(client):
    call_command('seed_sample_data')

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': 'not-a-date'},
        HTTP_HX_REQUEST='true',
    )
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Enter a valid arrival deadline.' in content
    assert 'id="deadline-error"' in content
    assert 'aria-invalid="true"' in content
    assert 'aria-describedby="deadline-error"' in content
    assert 'value="not-a-date"' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_dialog_requests_for_missing_cargo_return_not_found(client):
    call_command('seed_sample_data')

    response = client.get('/admin/cargo/MISSING1/destination/')

    assert response.status_code == 404


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_updates_cargo_refreshes_rows_and_completes(client):
    call_command('seed_sample_data')
    original = repository.find(TrackingId('DEF789'))
    assert original is not None

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'USDAL'},
        HTTP_HX_REQUEST='true',
    )
    content = response.content.decode()
    updated = repository.find(TrackingId('DEF789'))

    assert response.status_code == 200
    assert response['HX-Trigger-After-Swap'] == 'cargo-dialog-close'
    assert 'hx-swap-oob="outerHTML"' in content
    assert 'Dallas' in content
    assert 'data-tracking-id="DEF789"' in content
    assert 'id="cargo-edit-dialog"' not in content
    assert 'Widget for var' not in content
    assert updated is not None
    assert updated.route_specification.origin == original.route_specification.origin
    assert updated.route_specification.destination.unlocode.value == 'USDAL'
    assert (
        updated.route_specification.arrival_deadline
        == original.route_specification.arrival_deadline
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_updates_cargo_refreshes_rows_and_completes(client):
    call_command('seed_sample_data')
    original = repository.find(TrackingId('DEF789'))
    assert original is not None
    new_deadline = original.route_specification.arrival_deadline.date() + timedelta(days=10)

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': new_deadline.isoformat()},
        HTTP_HX_REQUEST='true',
    )
    content = response.content.decode()
    updated = repository.find(TrackingId('DEF789'))

    assert response.status_code == 200
    assert response['HX-Trigger-After-Swap'] == 'cargo-dialog-close'
    assert 'hx-swap-oob="outerHTML"' in content
    assert new_deadline.strftime('%m/%d/%Y') in content
    assert 'data-tracking-id="DEF789"' in content
    assert 'id="cargo-edit-dialog"' not in content
    assert 'Widget for var' not in content
    assert updated is not None
    assert updated.route_specification.origin == original.route_specification.origin
    assert updated.route_specification.destination == original.route_specification.destination
    assert updated.route_specification.arrival_deadline.date() == new_deadline
