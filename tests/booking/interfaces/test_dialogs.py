import re

import pytest
from django.core.management import call_command
from django.template.loader import render_to_string
from django.test import RequestFactory

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


@pytest.mark.django_db
def test_destination_dialog_shows_current_route_and_excludes_origin_and_destination():
    call_command('seed_sample_data')
    cargo_repository = DjangoCargoRepository()
    destination_view = create_destination_dialog_view(
        CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
        CargoDashboard(cargo_repository),
        DjangoLocationRepository().find_all,
    )

    response = destination_view(RequestFactory().get('/admin/cargo/DEF789/destination/'), 'DEF789')
    content = response.content.decode()
    options = re.search(r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', content, re.DOTALL)

    assert response.status_code == 200
    assert 'Hong Kong' in content and 'Melbourne' in content
    assert options is not None
    assert 'value="CNHKG"' not in options.group(1)
    assert 'value="AUMEL"' not in options.group(1)
    assert 'Update' in content and 'Cancel' in content


@pytest.mark.django_db
def test_destination_options_remain_stable_across_renders():
    call_command('seed_sample_data')
    cargo_repository = DjangoCargoRepository()
    locations = DjangoLocationRepository().find_all()
    original_locations = locations.copy()
    destination_view = create_destination_dialog_view(
        CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
        CargoDashboard(cargo_repository),
        lambda: locations,
    )

    responses = [
        destination_view(RequestFactory().get('/admin/cargo/DEF789/destination/'), 'DEF789')
        for _ in range(2)
    ]
    option_lists = [
        re.search(
            r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>',
            response.content.decode(),
            re.DOTALL,
        ).group(1)
        for response in responses
    ]

    assert option_lists[0] == option_lists[1]
    assert locations == original_locations


@pytest.mark.parametrize('destination', ['CNHKG', 'AUMEL'])
@pytest.mark.django_db
def test_destination_dialog_rejects_origin_or_current_destination(destination):
    call_command('seed_sample_data')
    cargo_repository = DjangoCargoRepository()
    tracking_id = TrackingId('DEF789')
    original = cargo_repository.find(tracking_id)
    assert original is not None
    destination_view = create_destination_dialog_view(
        CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
        CargoDashboard(cargo_repository),
        DjangoLocationRepository().find_all,
    )

    response = destination_view(
        RequestFactory().post(
            '/admin/cargo/DEF789/destination/',
            {'destination': destination},
        ),
        'DEF789',
    )
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Select a valid destination.' in content
    assert cargo_repository.find(tracking_id) == original


@pytest.mark.django_db
def test_unknown_cargo_dialog_renders_not_found_feedback():
    call_command('seed_sample_data')
    cargo_repository = DjangoCargoRepository()
    destination_view = create_destination_dialog_view(
        CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
        CargoDashboard(cargo_repository),
        DjangoLocationRepository().find_all,
    )

    response = destination_view(
        RequestFactory().get('/admin/cargo/UNKNOWN/destination/'), 'UNKNOWN'
    )
    content = response.content.decode()

    assert response.status_code == 404
    assert 'role="alert"' in content
    assert 'Cargo with tracking ID UNKNOWN was not found.' in content


@pytest.mark.django_db
def test_destination_dialog_updates_through_specification_and_refreshes_dashboard():
    call_command('seed_sample_data')
    cargo_repository = DjangoCargoRepository()
    tracking_id = TrackingId('DEF789')
    original = cargo_repository.find(tracking_id)
    assert original is not None
    destination_view = create_destination_dialog_view(
        CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
        CargoDashboard(cargo_repository),
        DjangoLocationRepository().find_all,
    )

    response = destination_view(
        RequestFactory().post(
            '/admin/cargo/DEF789/destination/',
            {'destination': 'USNYC'},
            HTTP_HX_REQUEST='true',
        ),
        'DEF789',
    )
    updated = cargo_repository.find(tracking_id)
    dashboard_view, _ = create_booking_views(CargoDashboard(cargo_repository))
    refreshed_dashboard = dashboard_view(RequestFactory().get('/admin/dashboard/')).content.decode()

    assert response.status_code == 200
    assert response['HX-Redirect'] == '/admin/dashboard/'
    assert updated is not None
    assert updated.route_specification.origin == original.route_specification.origin
    assert updated.route_specification.destination.unlocode.value == 'USNYC'
    assert (
        updated.route_specification.arrival_deadline
        == original.route_specification.arrival_deadline
    )
    assert updated.itinerary == original.itinerary
    assert 'Widget for var' not in response.content.decode()
    assert 'New York' in refreshed_dashboard


@pytest.mark.django_db
def test_deadline_dialog_shows_parse_error_without_changing_cargo():
    call_command('seed_sample_data')
    cargo_repository = DjangoCargoRepository()
    tracking_id = TrackingId('DEF789')
    original = cargo_repository.find(tracking_id)
    assert original is not None
    deadline_view = create_deadline_dialog_view(
        CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
        CargoDashboard(cargo_repository),
    )

    response = deadline_view(
        RequestFactory().post(
            '/admin/cargo/DEF789/deadline/',
            {'arrival_deadline': 'not-a-date'},
            HTTP_HX_REQUEST='true',
        ),
        'DEF789',
    )

    assert response.status_code == 200
    assert 'id="deadline-error"' in response.content.decode()
    assert 'Enter a valid arrival deadline.' in response.content.decode()
    assert cargo_repository.find(tracking_id) == original


@pytest.mark.django_db
def test_deadline_dialog_updates_and_refreshes_without_changing_route_endpoints():
    call_command('seed_sample_data')
    cargo_repository = DjangoCargoRepository()
    tracking_id = TrackingId('DEF789')
    original = cargo_repository.find(tracking_id)
    assert original is not None
    deadline_view = create_deadline_dialog_view(
        CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
        CargoDashboard(cargo_repository),
    )

    initial_response = deadline_view(
        RequestFactory().get('/admin/cargo/DEF789/deadline/'), 'DEF789'
    )
    response = deadline_view(
        RequestFactory().post(
            '/admin/cargo/DEF789/deadline/',
            {'arrival_deadline': '2027-01-15'},
            HTTP_HX_REQUEST='true',
        ),
        'DEF789',
    )
    updated = cargo_repository.find(tracking_id)
    dashboard_view, _ = create_booking_views(CargoDashboard(cargo_repository))
    refreshed_dashboard = dashboard_view(RequestFactory().get('/admin/dashboard/')).content.decode()

    assert initial_response.status_code == 200
    assert (
        f'value="{original.route_specification.arrival_deadline.date().isoformat()}"'
        in initial_response.content.decode()
    )
    assert 'Hong Kong' in initial_response.content.decode()
    assert 'Melbourne' in initial_response.content.decode()
    assert response.status_code == 200
    assert response['HX-Redirect'] == '/admin/dashboard/'
    assert updated is not None
    assert updated.route_specification.origin == original.route_specification.origin
    assert updated.route_specification.destination == original.route_specification.destination
    assert updated.route_specification.arrival_deadline.date().isoformat() == '2027-01-15'
    assert updated.itinerary == original.itinerary
    assert 'Widget for var' not in response.content.decode()
    assert '01/15/2027' in refreshed_dashboard


@pytest.mark.django_db
def test_not_routed_table_opens_destination_and_deadline_dialogs():
    call_command('seed_sample_data')
    cargo = DjangoCargoRepository().find(TrackingId('DEF789'))
    assert cargo is not None

    content = render_to_string(
        'booking/dashboard/not_routed_table.html',
        {'not_routed_cargos': [cargo]},
    )

    assert 'href="/admin/cargo/DEF789/route/"' in content
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in content
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in content
    assert 'id="cargo-edit-dialog"' in content
    assert 'this.showModal()' in content
