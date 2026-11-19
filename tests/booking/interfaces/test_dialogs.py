import re
from types import SimpleNamespace

import pytest
from django.core.management import call_command
from django.http import Http404
from django.template.loader import render_to_string
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


def _dialog_views():
    cargo_repository = DjangoCargoRepository()
    return create_booking_dialog_views(
        CargoDashboard(cargo_repository),
        CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
        DjangoLocationRepository().find_all,
    )


def destination_dialog(request, tracking_id):
    return _dialog_views()[0](request, tracking_id)


def deadline_dialog(request, tracking_id):
    return _dialog_views()[1](request, tracking_id)


def dashboard(request):
    return create_booking_views(CargoDashboard(DjangoCargoRepository()))[0](request)


urlpatterns = [
    path('admin/dashboard/', dashboard),
    path('admin/cargo/<str:tracking_id>/destination/', destination_dialog),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_dialog),
]


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_http_flow_opens_updates_and_refreshes_destination_dialog(client):
    call_command('seed_sample_data')

    dashboard_response = client.get('/admin/dashboard/')
    dialog_response = client.get(
        '/admin/cargo/DEF789/destination/',
        HTTP_HX_REQUEST='true',
    )
    update_response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'USCHI'},
        HTTP_HX_REQUEST='true',
    )
    refreshed_dashboard = client.get('/admin/dashboard/')
    not_routed_table = (
        refreshed_dashboard.content.decode()
        .split('id="not-routed-cargo"', 1)[1]
        .split('</section>', 1)[0]
    )

    assert dashboard_response.status_code == 200
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in dashboard_response.content.decode()
    assert dialog_response.status_code == 200
    assert '<dialog' in dialog_response.content.decode()
    assert update_response.status_code == 200
    assert update_response.headers['HX-Redirect'] == '/admin/dashboard/'
    assert 'USCHI' in not_routed_table
    assert 'Change destination' in not_routed_table


@pytest.mark.django_db
def test_not_routed_table_opens_destination_and_deadline_dialogs():
    call_command('seed_sample_data')
    dashboard = CargoDashboard(DjangoCargoRepository()).get_dashboard()

    content = render_to_string(
        'booking/dashboard/not_routed_table.html',
        {'not_routed_cargos': dashboard.not_routed_cargos},
    )

    assert 'href="/admin/cargo/DEF789/route/"' in content
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in content
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in content
    assert 'id="booking-dialog"' in content
    assert 'hx-on::before-swap=' in content


@pytest.mark.django_db
def test_destination_dialog_excludes_origin_and_current_destination_without_mutating_locations():
    call_command('seed_sample_data')
    cargo_repository = DjangoCargoRepository()
    location_repository = DjangoLocationRepository()
    locations = location_repository.find_all()
    original_locations = locations.copy()
    destination_view, _ = create_booking_dialog_views(
        CargoDashboard(cargo_repository),
        CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
        lambda: locations,
    )
    request = RequestFactory().get('/admin/cargo/DEF789/destination/')
    request.user = SimpleNamespace(is_authenticated=False)

    response = destination_view(request, 'DEF789')
    content = response.content.decode()
    options = re.search(r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', content, re.DOTALL)
    repeated_content = destination_view(request, 'DEF789').content.decode()
    repeated_options = re.search(
        r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>',
        repeated_content,
        re.DOTALL,
    )

    assert response.status_code == 200
    assert options is not None
    assert repeated_options is not None
    assert repeated_options.group(1) == options.group(1)
    assert 'Hong Kong to Melbourne' in content
    assert 'value="CNHKG"' not in options.group(1)
    assert 'value="AUMEL"' not in options.group(1)
    assert 'value="USCHI"' in options.group(1)
    assert locations == original_locations


@pytest.mark.django_db
def test_invalid_destination_is_rejected_without_changing_cargo_or_locations():
    call_command('seed_sample_data')
    cargo_repository = DjangoCargoRepository()
    location_repository = DjangoLocationRepository()
    locations = location_repository.find_all()
    original_locations = locations.copy()
    destination_view, _ = create_booking_dialog_views(
        CargoDashboard(cargo_repository),
        CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
        lambda: locations,
    )
    request = RequestFactory().post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'CNHKG'},
        HTTP_HX_REQUEST='true',
    )
    request.user = SimpleNamespace(is_authenticated=False)

    response = destination_view(request, 'DEF789')
    content = response.content.decode()
    cargo = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 200
    assert 'Select a valid destination.' in content
    assert cargo is not None
    assert cargo.route_specification.destination.unlocode.value == 'AUMEL'
    assert locations == original_locations


@pytest.mark.django_db
def test_deadline_dialog_displays_current_deadline_and_route():
    call_command('seed_sample_data')
    cargo_repository = DjangoCargoRepository()
    _, deadline_view = create_booking_dialog_views(
        CargoDashboard(cargo_repository),
        CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
        DjangoLocationRepository().find_all,
    )
    request = RequestFactory().get('/admin/cargo/DEF789/deadline/')
    request.user = SimpleNamespace(is_authenticated=False)

    response = deadline_view(request, 'DEF789')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Hong Kong to Melbourne' in content
    assert 'value="2027-01-19"' in content
    assert 'id="deadline-error"' not in content


@pytest.mark.django_db
def test_missing_cargo_returns_not_found_for_both_dialogs():
    cargo_repository = DjangoCargoRepository()
    destination_view, deadline_view = create_booking_dialog_views(
        CargoDashboard(cargo_repository),
        CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
        DjangoLocationRepository().find_all,
    )
    request = RequestFactory().get('/admin/cargo/UNKNOWN/destination/')
    request.user = SimpleNamespace(is_authenticated=False)

    with pytest.raises(Http404, match='Cargo with tracking ID UNKNOWN not found.'):
        destination_view(request, 'UNKNOWN')
    with pytest.raises(Http404, match='Cargo with tracking ID UNKNOWN not found.'):
        deadline_view(request, 'UNKNOWN')


@pytest.mark.django_db
def test_invalid_deadline_shows_field_error_and_keeps_entered_value():
    call_command('seed_sample_data')
    cargo_repository = DjangoCargoRepository()
    _, deadline_view = create_booking_dialog_views(
        CargoDashboard(cargo_repository),
        CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
        DjangoLocationRepository().find_all,
    )
    request = RequestFactory().post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': 'not-a-date'},
        HTTP_HX_REQUEST='true',
    )
    request.user = SimpleNamespace(is_authenticated=False)

    response = deadline_view(request, 'DEF789')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Enter a valid arrival deadline.' in content
    assert 'value="not-a-date"' in content


@pytest.mark.django_db
def test_missing_deadline_shows_field_error_and_empty_value():
    call_command('seed_sample_data')
    cargo_repository = DjangoCargoRepository()
    _, deadline_view = create_booking_dialog_views(
        CargoDashboard(cargo_repository),
        CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
        DjangoLocationRepository().find_all,
    )
    request = RequestFactory().post('/admin/cargo/DEF789/deadline/', {}, HTTP_HX_REQUEST='true')
    request.user = SimpleNamespace(is_authenticated=False)

    response = deadline_view(request, 'DEF789')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Enter a valid arrival deadline.' in content
    assert 'value=""' in content


@pytest.mark.django_db
def test_deadline_update_preserves_other_route_specification_fields_and_redirects():
    call_command('seed_sample_data')
    cargo_repository = DjangoCargoRepository()
    cargo_before = cargo_repository.find(TrackingId('DEF789'))
    assert cargo_before is not None
    _, deadline_view = create_booking_dialog_views(
        CargoDashboard(cargo_repository),
        CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
        DjangoLocationRepository().find_all,
    )
    request = RequestFactory().post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': '2027-01-03'},
    )
    request.user = SimpleNamespace(is_authenticated=False)

    response = deadline_view(request, 'DEF789')
    updated_cargo = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 302
    assert response.headers['Location'] == '/admin/dashboard/'
    assert updated_cargo is not None
    assert updated_cargo.route_specification.origin == cargo_before.route_specification.origin
    assert (
        updated_cargo.route_specification.destination
        == cargo_before.route_specification.destination
    )
    assert updated_cargo.route_specification.arrival_deadline.date().isoformat() == '2027-01-03'
    refreshed_table = render_to_string(
        'booking/dashboard/not_routed_table.html',
        {'not_routed_cargos': CargoDashboard(cargo_repository).get_dashboard().not_routed_cargos},
    )
    assert '01/03/2027' in refreshed_table


@pytest.mark.django_db
def test_destination_update_preserves_other_route_specification_fields_and_redirects():
    call_command('seed_sample_data')
    cargo_repository = DjangoCargoRepository()
    cargo_before = cargo_repository.find(TrackingId('DEF789'))
    assert cargo_before is not None
    destination_view, _ = create_booking_dialog_views(
        CargoDashboard(cargo_repository),
        CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
        DjangoLocationRepository().find_all,
    )
    request = RequestFactory().post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'USCHI'},
        HTTP_HX_REQUEST='true',
    )
    request.user = SimpleNamespace(is_authenticated=False)

    response = destination_view(request, 'DEF789')
    updated_cargo = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 200
    assert response.headers['HX-Redirect'] == '/admin/dashboard/'
    assert updated_cargo is not None
    assert updated_cargo.route_specification.origin == cargo_before.route_specification.origin
    assert updated_cargo.route_specification.destination.unlocode.value == 'USCHI'
    assert (
        updated_cargo.route_specification.arrival_deadline
        == cargo_before.route_specification.arrival_deadline
    )
    refreshed_table = render_to_string(
        'booking/dashboard/not_routed_table.html',
        {'not_routed_cargos': CargoDashboard(cargo_repository).get_dashboard().not_routed_cargos},
    )
    assert 'USCHI' in refreshed_table
