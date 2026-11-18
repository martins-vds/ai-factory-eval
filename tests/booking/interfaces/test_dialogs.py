import re
from datetime import datetime

import pytest
from django.core.management import call_command
from django.shortcuts import render
from django.template.loader import render_to_string
from django.test import RequestFactory, override_settings
from django.urls import path
from django.utils import timezone

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.booking.interfaces.dialogs.views import create_booking_dialog_views
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository

_e2e_cargo_repository = DjangoCargoRepository()
_e2e_destination_view, _e2e_deadline_view = create_booking_dialog_views(
    CargoDashboard(_e2e_cargo_repository),
    CargoSpecification(_e2e_cargo_repository, DjangoHandlingEventRepository()),
    DjangoLocationRepository().find_all,
)


def _create_dialog_views(locations):
    cargo_repository = DjangoCargoRepository()
    return create_booking_dialog_views(
        CargoDashboard(cargo_repository),
        CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
        lambda: locations,
    )


def _dashboard_table(request):
    dashboard = CargoDashboard(DjangoCargoRepository()).get_dashboard()
    return render(
        request,
        'booking/dashboard/not_routed_table.html',
        {'not_routed_cargos': dashboard.not_routed_cargos},
    )


urlpatterns = [
    path('admin/dashboard/', _dashboard_table),
    path('admin/cargo/<str:tracking_id>/destination/', _e2e_destination_view),
    path('admin/cargo/<str:tracking_id>/deadline/', _e2e_deadline_view),
]


@pytest.mark.django_db
def test_destination_dialog_shows_current_specification_and_stable_filtered_options():
    call_command('seed_sample_data')
    backing_locations = DjangoLocationRepository().find_all()
    change_destination, _ = _create_dialog_views(backing_locations)
    request = RequestFactory().get('/admin/cargo/DEF789/destination/')

    first_response = change_destination(request, 'DEF789')
    second_response = change_destination(request, 'DEF789')
    first_content = first_response.content.decode()
    second_content = second_response.content.decode()
    options = re.search(
        r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', first_content, re.DOTALL
    )
    second_options = re.search(
        r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', second_content, re.DOTALL
    )

    assert first_response.status_code == 200
    assert 'Hong Kong' in first_content and 'CNHKG' in first_content
    assert 'Melbourne' in first_content and 'AUMEL' in first_content
    assert options is not None
    assert 'value="CNHKG"' not in options.group(1)
    assert 'value="AUMEL"' not in options.group(1)
    assert options.group(1).count('<option') == len(backing_locations) - 1
    assert second_options is not None
    assert options.group(1) == second_options.group(1)
    assert len(backing_locations) == 13
    assert backing_locations == DjangoLocationRepository().find_all()
    assert '<form method="dialog"' in first_content
    assert 'Cancel' in first_content


@pytest.mark.django_db
def test_deadline_dialog_shows_current_specification_and_deadline():
    call_command('seed_sample_data')
    _, change_deadline = _create_dialog_views(DjangoLocationRepository().find_all())
    request = RequestFactory().get('/admin/cargo/DEF789/deadline/')

    response = change_deadline(request, 'DEF789')
    content = response.content.decode()
    deadline_input = re.search(r'<input\b[^>]*name="deadline"[^>]*>', content)

    assert response.status_code == 200
    assert 'Hong Kong' in content and 'CNHKG' in content
    assert 'Melbourne' in content and 'AUMEL' in content
    assert 'name="deadline"' in content
    assert deadline_input is not None
    assert 'value="2027-01-18"' in deadline_input.group()
    assert '<form method="dialog"' in content
    assert 'Cancel' in content


@pytest.mark.django_db
def test_invalid_deadline_shows_field_error_without_updating_cargo():
    call_command('seed_sample_data')
    cargo_repository = DjangoCargoRepository()
    _, change_deadline = _create_dialog_views(DjangoLocationRepository().find_all())
    tracking_id = TrackingId('DEF789')
    original = cargo_repository.find(tracking_id)
    assert original is not None

    response = change_deadline(
        RequestFactory().post(
            '/admin/cargo/DEF789/deadline/',
            {'deadline': 'not-a-date'},
        ),
        'DEF789',
    )
    updated = cargo_repository.find(tracking_id)
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Enter a valid arrival deadline.' in content
    assert 'aria-invalid="true"' in content
    assert 'id="deadline-error"' in content
    assert 'value="not-a-date"' in content
    assert updated is not None
    assert updated.route_specification == original.route_specification


@pytest.mark.django_db
def test_destination_update_preserves_other_route_fields_and_refreshes_table():
    call_command('seed_sample_data')
    cargo_repository = DjangoCargoRepository()
    change_destination, _ = _create_dialog_views(DjangoLocationRepository().find_all())
    tracking_id = TrackingId('DEF789')
    original = cargo_repository.find(tracking_id)
    assert original is not None

    response = change_destination(
        RequestFactory().post(
            '/admin/cargo/DEF789/destination/',
            {'destination': 'USNYC'},
        ),
        'DEF789',
    )
    updated = cargo_repository.find(tracking_id)
    content = response.content.decode()

    assert response.status_code == 200
    assert updated is not None
    assert updated.route_specification.origin == original.route_specification.origin
    assert updated.route_specification.destination.unlocode.value == 'USNYC'
    assert (
        updated.route_specification.arrival_deadline
        == original.route_specification.arrival_deadline
    )
    assert 'New York' in content and 'USNYC' in content
    assert 'data-tracking-id="DEF789"' in content
    assert 'hx-swap-oob="outerHTML"' in content
    assert response['HX-Reswap'] == 'none'
    assert 'Widget for var' not in content


@pytest.mark.django_db
def test_deadline_update_preserves_other_route_fields_and_refreshes_table():
    call_command('seed_sample_data')
    cargo_repository = DjangoCargoRepository()
    _, change_deadline = _create_dialog_views(DjangoLocationRepository().find_all())
    tracking_id = TrackingId('DEF789')
    original = cargo_repository.find(tracking_id)
    assert original is not None
    deadline = datetime(2027, 2, 1)

    response = change_deadline(
        RequestFactory().post(
            '/admin/cargo/DEF789/deadline/',
            {'deadline': deadline.date().isoformat()},
        ),
        'DEF789',
    )
    updated = cargo_repository.find(tracking_id)
    content = response.content.decode()

    assert response.status_code == 200
    assert updated is not None
    assert updated.route_specification.origin == original.route_specification.origin
    assert updated.route_specification.destination == original.route_specification.destination
    assert updated.route_specification.arrival_deadline == timezone.make_aware(deadline)
    assert 'data-tracking-id="DEF789"' in content
    assert '02/01/2027' in content
    assert 'hx-swap-oob="outerHTML"' in content
    assert response['HX-Reswap'] == 'none'
    assert 'Widget for var' not in content


@pytest.mark.django_db
def test_not_routed_table_opens_both_dialogs_and_renders_htmx_errors():
    call_command('seed_sample_data')
    dashboard = CargoDashboard(DjangoCargoRepository()).get_dashboard()
    content = render_to_string(
        'booking/dashboard/not_routed_table.html',
        {'not_routed_cargos': dashboard.not_routed_cargos},
        request=RequestFactory().get('/admin/dashboard/'),
    )
    row = content.split('data-tracking-id="DEF789"', 1)[1].split('</tr>', 1)[0]

    assert 'Change destination' in row
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in row
    assert 'Change deadline' in row
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in row
    assert 'hx-target="#booking-dialog"' in row
    assert 'hx-on::after-swap' in content
    assert 'hx-on::before-swap' in content


@pytest.mark.django_db
def test_stale_dialog_request_renders_an_error_fragment():
    call_command('seed_sample_data')
    change_destination, change_deadline = _create_dialog_views(
        DjangoLocationRepository().find_all()
    )

    destination_response = change_destination(
        RequestFactory().get(
            '/admin/cargo/MISSING/destination/',
            HTTP_HX_REQUEST='true',
        ),
        'MISSING',
    )
    response = change_deadline(
        RequestFactory().get(
            '/admin/cargo/MISSING/deadline/',
            HTTP_HX_REQUEST='true',
        ),
        'MISSING',
    )

    assert destination_response.status_code == 404
    assert 'role="alert"' in destination_response.content.decode()
    assert 'Cargo not found' in destination_response.content.decode()
    assert response.status_code == 404
    assert 'role="alert"' in response.content.decode()
    assert 'Cargo not found' in response.content.decode()


@pytest.mark.django_db
def test_dialogs_reject_unsupported_methods():
    call_command('seed_sample_data')
    change_destination, change_deadline = _create_dialog_views(
        DjangoLocationRepository().find_all()
    )

    destination_response = change_destination(
        RequestFactory().put('/admin/cargo/DEF789/destination/'),
        'DEF789',
    )
    deadline_response = change_deadline(
        RequestFactory().put('/admin/cargo/DEF789/deadline/'),
        'DEF789',
    )

    assert destination_response.status_code == 405
    assert destination_response['Allow'] == 'GET, POST'
    assert deadline_response.status_code == 405
    assert deadline_response['Allow'] == 'GET, POST'


@pytest.mark.django_db
def test_invalid_destination_shows_field_error_without_updating_cargo():
    call_command('seed_sample_data')
    cargo_repository = DjangoCargoRepository()
    change_destination, _ = _create_dialog_views(DjangoLocationRepository().find_all())
    tracking_id = TrackingId('DEF789')
    original = cargo_repository.find(tracking_id)
    assert original is not None

    response = change_destination(
        RequestFactory().post(
            '/admin/cargo/DEF789/destination/',
            {'destination': 'UNKNOWN'},
        ),
        'DEF789',
    )
    updated = cargo_repository.find(tracking_id)
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Select a valid destination.' in content
    assert 'aria-invalid="true"' in content
    assert 'id="destination-error"' in content
    assert 'Hong Kong' in content and 'CNHKG' in content
    assert 'Melbourne' in content and 'AUMEL' in content
    assert 'value="USNYC"' in content
    assert updated is not None
    assert updated.route_specification == original.route_specification


@pytest.mark.django_db
def test_missing_destination_shows_error_and_keeps_empty_option_selected():
    call_command('seed_sample_data')
    cargo_repository = DjangoCargoRepository()
    change_destination, _ = _create_dialog_views(DjangoLocationRepository().find_all())
    tracking_id = TrackingId('DEF789')
    original = cargo_repository.find(tracking_id)
    assert original is not None

    response = change_destination(
        RequestFactory().post('/admin/cargo/DEF789/destination/'),
        'DEF789',
    )
    updated = cargo_repository.find(tracking_id)
    content = response.content.decode()

    assert 'Select a valid destination.' in content
    assert '<option value="" selected>' in content
    assert updated is not None
    assert updated.route_specification == original.route_specification


@pytest.mark.django_db
def test_missing_deadline_shows_error_and_keeps_field_empty():
    call_command('seed_sample_data')
    _, change_deadline = _create_dialog_views(DjangoLocationRepository().find_all())

    response = change_deadline(
        RequestFactory().post('/admin/cargo/DEF789/deadline/'),
        'DEF789',
    )
    content = response.content.decode()
    deadline_input = re.search(r'<input\b[^>]*name="deadline"[^>]*>', content)

    assert 'Enter a valid arrival deadline.' in content
    assert 'aria-invalid="true"' in content
    assert deadline_input is not None
    assert 'value=""' in deadline_input.group()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_dashboard_dialog_flows_update_cargo_and_refreshed_table(client):
    call_command('seed_sample_data')

    dashboard_response = client.get('/admin/dashboard/')
    dialog_response = client.get(
        '/admin/cargo/DEF789/destination/',
        HTTP_HX_REQUEST='true',
    )
    update_response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'USNYC'},
        HTTP_HX_REQUEST='true',
    )
    refreshed_dashboard = client.get('/admin/dashboard/')
    refreshed_row = (
        refreshed_dashboard.content.decode()
        .split('data-tracking-id="DEF789"', 1)[1]
        .split('</tr>', 1)[0]
    )
    deadline_dialog = client.get(
        '/admin/cargo/DEF789/deadline/',
        HTTP_HX_REQUEST='true',
    )
    deadline_update = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': '2027-02-01'},
        HTTP_HX_REQUEST='true',
    )
    deadline_refreshed_dashboard = client.get('/admin/dashboard/')
    deadline_refreshed_row = (
        deadline_refreshed_dashboard.content.decode()
        .split('data-tracking-id="DEF789"', 1)[1]
        .split('</tr>', 1)[0]
    )

    assert 'hx-get="/admin/cargo/DEF789/destination/"' in dashboard_response.content.decode()
    assert dialog_response.status_code == 200
    assert 'Change destination' in dialog_response.content.decode()
    assert update_response.status_code == 200
    assert update_response['HX-Reswap'] == 'none'
    assert 'hx-swap-oob="outerHTML"' in update_response.content.decode()
    assert 'New York' in refreshed_row and 'USNYC' in refreshed_row
    assert deadline_dialog.status_code == 200
    assert 'value="2027-01-18"' in deadline_dialog.content.decode()
    assert deadline_update.status_code == 200
    assert deadline_update['HX-Reswap'] == 'none'
    assert '02/01/2027' in deadline_refreshed_row
