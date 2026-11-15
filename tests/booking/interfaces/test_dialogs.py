import re
from datetime import UTC, date, datetime, time
from types import SimpleNamespace

import pytest
from django.core.management import call_command
from django.test import RequestFactory, override_settings
from django.urls import path
from django.utils import timezone

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.booking.interfaces.dialogs.views import create_dialog_views
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository


def _create_dialog_views(list_shipping_locations=None):
    cargo_repository = DjangoCargoRepository()
    dashboard = CargoDashboard(cargo_repository)
    specification = CargoSpecification(
        cargo_repository,
        DjangoHandlingEventRepository(),
    )
    return create_dialog_views(
        dashboard,
        specification,
        list_shipping_locations or DjangoLocationRepository().find_all,
    )


destination_dialog_view, deadline_dialog_view = _create_dialog_views()
dashboard_view, _ = create_booking_views(CargoDashboard(DjangoCargoRepository()))
urlpatterns = [
    path('admin/cargo/<str:tracking_id>/destination/', destination_dialog_view),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_dialog_view),
    path('admin/dashboard/', dashboard_view),
]


def _cargo(tracking_id='DEF789'):
    cargo = DjangoCargoRepository().find(TrackingId(tracking_id))
    assert cargo is not None
    return cargo


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_not_routed_table_opens_destination_and_deadline_dialogs(client):
    call_command('seed_sample_data')

    response = client.get('/admin/dashboard/')
    content = response.content.decode()
    not_routed_table = content.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]

    assert response.status_code == 200
    assert 'data-tracking-id="DEF789"' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in not_routed_table
    assert 'id="booking-dialog"' in not_routed_table
    assert 'href="/admin/cargo/DEF789/route/"' in not_routed_table


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_shows_current_values_and_filters_without_mutating_locations():
    call_command('seed_sample_data')
    locations = DjangoLocationRepository().find_all()
    original_locations = list(locations)
    view, _ = _create_dialog_views(lambda: locations)
    request = RequestFactory().get('/admin/cargo/DEF789/destination/')
    request.user = SimpleNamespace(is_authenticated=False)

    response = view(request, 'DEF789')
    content = response.content.decode()
    options = re.search(r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', content, re.DOTALL)
    cargo = _cargo()

    assert response.status_code == 200
    assert cargo.route_specification.origin.name in content
    assert cargo.route_specification.destination.name in content
    assert 'type="button" onclick="this.closest(\'dialog\').close()"' in content
    assert options is not None
    assert f'value="{cargo.route_specification.origin.unlocode.value}"' not in options.group(1)
    assert f'value="{cargo.route_specification.destination.unlocode.value}"' not in options.group(1)
    assert locations == original_locations

    second_response = view(request, 'DEF789')
    assert second_response.status_code == 200
    assert locations == original_locations


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_shows_current_deadline_and_reports_parse_errors(client):
    call_command('seed_sample_data')
    cargo = _cargo()
    deadline = cargo.route_specification.arrival_deadline.date().isoformat()

    response = client.get('/admin/cargo/DEF789/deadline/')
    content = response.content.decode()

    assert response.status_code == 200
    assert cargo.route_specification.origin.name in content
    assert cargo.route_specification.destination.name in content
    assert 'type="date"' in content
    assert f'value="{deadline}"' in content

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': 'not-a-date'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert 'Enter a valid arrival deadline.' in response.content.decode()
    assert 'value="not-a-date"' in response.content.decode()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_update_preserves_other_route_fields_and_refreshes_table(client):
    call_command('seed_sample_data')
    cargo = _cargo()
    locations = DjangoLocationRepository().find_all()
    destination = next(
        location
        for location in locations
        if location not in (cargo.route_specification.origin, cargo.route_specification.destination)
    )

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': destination.unlocode.value},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert response.headers['HX-Redirect'] == '/admin/dashboard/'

    updated = _cargo()
    assert updated.route_specification.origin == cargo.route_specification.origin
    assert updated.route_specification.destination == destination
    assert (
        updated.route_specification.arrival_deadline == cargo.route_specification.arrival_deadline
    )

    refreshed = client.get('/admin/dashboard/').content.decode()
    not_routed_table = refreshed.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]
    assert destination.name in not_routed_table
    assert 'widget' not in response.content.decode().lower()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_update_preserves_other_route_fields_and_refreshes_table(client):
    call_command('seed_sample_data')
    cargo = _cargo()
    new_deadline = datetime.combine(date(2032, 1, 2), time.min, tzinfo=UTC)

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': new_deadline.date().isoformat()},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert response.headers['HX-Redirect'] == '/admin/dashboard/'

    updated = _cargo()
    assert updated.route_specification.origin == cargo.route_specification.origin
    assert updated.route_specification.destination == cargo.route_specification.destination
    assert updated.route_specification.arrival_deadline == timezone.make_aware(
        datetime.combine(new_deadline.date(), time.min)
    )

    refreshed = client.get('/admin/dashboard/').content.decode()
    not_routed_table = refreshed.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]
    assert '01/02/2032' in not_routed_table


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_dialogs_return_not_found_for_unknown_cargo(client):
    response = client.get('/admin/cargo/MISSING1/destination/')

    assert response.status_code == 404


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_reports_invalid_location(client):
    call_command('seed_sample_data')

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'UNKNOWN'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert 'Select a valid destination.' in response.content.decode()
