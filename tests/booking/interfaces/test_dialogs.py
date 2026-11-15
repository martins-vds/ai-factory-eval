import re
from datetime import UTC, datetime

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
from cargotracker.location.domain.un_locode import UnLocode


cargo_repository = DjangoCargoRepository()
dashboard = CargoDashboard(cargo_repository)
specification = CargoSpecification(cargo_repository, DjangoHandlingEventRepository())
dashboard_view, _ = create_booking_views(dashboard)
destination_view, deadline_view = create_booking_dialog_views(
    dashboard,
    specification,
    DjangoLocationRepository().find_all,
)
urlpatterns = [
    path('admin/dashboard/', dashboard_view),
    path('admin/cargo/<str:tracking_id>/destination/', destination_view),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_view),
]


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_shows_current_values_and_stable_filtered_options(client):
    call_command('seed_sample_data')

    first_response = client.get(
        '/admin/cargo/DEF789/destination/',
        HTTP_HX_REQUEST='true',
    )
    second_response = client.get(
        '/admin/cargo/DEF789/destination/',
        HTTP_HX_REQUEST='true',
    )
    first_content = first_response.content.decode()
    options = re.search(
        r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', first_content, re.DOTALL
    )
    repeated_options = re.search(
        r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>',
        second_response.content.decode(),
        re.DOTALL,
    )

    assert first_response.status_code == 200
    assert 'Hong Kong' in first_content
    assert 'Melbourne' in first_content
    assert options is not None
    assert repeated_options is not None
    option_codes = re.findall(r'<option\b[^>]*value="([^"]+)"', options.group(1))
    assert len(option_codes) == 11
    assert 'CNHKG' not in option_codes
    assert 'AUMEL' not in option_codes
    assert options.group(1) == repeated_options.group(1)


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_shows_current_route_and_deadline(client, monkeypatch):
    monkeypatch.setattr(
        'django.utils.timezone.now',
        lambda: datetime(2026, 11, 15, 12, tzinfo=UTC),
    )
    call_command('seed_sample_data')

    response = client.get('/admin/cargo/DEF789/deadline/', HTTP_HX_REQUEST='true')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Hong Kong' in content
    assert 'Melbourne' in content
    assert 'value="2027-01-15"' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_reports_a_field_error_for_unparseable_date(client):
    call_command('seed_sample_data')

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'action': 'update', 'deadline': 'not-a-date'},
        HTTP_HX_REQUEST='true',
    )
    content = response.content.decode()
    cargo = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 200
    assert 'Enter a valid arrival deadline.' in content
    assert 'aria-invalid="true"' in content
    assert 'value="not-a-date"' in content
    assert cargo is not None
    assert cargo.route_specification.arrival_deadline.date().isoformat() == '2027-01-15'


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_update_preserves_other_specification_fields_and_refreshes(client):
    call_command('seed_sample_data')
    cargo_before = cargo_repository.find(TrackingId('DEF789'))
    assert cargo_before is not None

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'action': 'update', 'destination': 'USNYC'},
        HTTP_HX_REQUEST='true',
    )
    updated_cargo = cargo_repository.find(TrackingId('DEF789'))
    dashboard_content = client.get('/admin/dashboard/').content.decode()
    not_routed_table = dashboard_content.split('id="not-routed-cargo"', 1)[1].split(
        '</section>', 1
    )[0]

    assert response.status_code == 204
    assert response['HX-Refresh'] == 'true'
    assert updated_cargo is not None
    assert updated_cargo.route_specification.origin == cargo_before.route_specification.origin
    assert updated_cargo.route_specification.destination == DjangoLocationRepository().find(
        UnLocode('USNYC')
    )
    assert (
        updated_cargo.route_specification.arrival_deadline
        == cargo_before.route_specification.arrival_deadline
    )
    assert 'data-tracking-id="DEF789"' in not_routed_table
    assert 'New York' in not_routed_table
    assert 'USNYC' in not_routed_table


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_update_preserves_route_and_refreshes(client):
    call_command('seed_sample_data')
    cargo_before = cargo_repository.find(TrackingId('DEF789'))
    assert cargo_before is not None

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'action': 'update', 'deadline': '2027-01-20'},
        HTTP_HX_REQUEST='true',
    )
    updated_cargo = cargo_repository.find(TrackingId('DEF789'))
    dashboard_content = client.get('/admin/dashboard/').content.decode()
    not_routed_table = dashboard_content.split('id="not-routed-cargo"', 1)[1].split(
        '</section>', 1
    )[0]

    assert response.status_code == 204
    assert response['HX-Refresh'] == 'true'
    assert updated_cargo is not None
    assert updated_cargo.route_specification.origin == cargo_before.route_specification.origin
    assert (
        updated_cargo.route_specification.destination
        == cargo_before.route_specification.destination
    )
    assert updated_cargo.route_specification.arrival_deadline == datetime(
        2027, 1, 20, tzinfo=UTC
    )
    assert '01/20/2027' in not_routed_table


@pytest.mark.parametrize(
    'endpoint',
    ('destination', 'deadline'),
)
@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_cancel_dialog_closes_without_updating_cargo(client, endpoint):
    call_command('seed_sample_data')
    cargo_before = cargo_repository.find(TrackingId('DEF789'))
    assert cargo_before is not None

    response = client.post(
        f'/admin/cargo/DEF789/{endpoint}/',
        {'action': 'cancel'},
        HTTP_HX_REQUEST='true',
    )
    cargo_after = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 200
    assert response.content == b''
    assert 'HX-Refresh' not in response
    assert cargo_after == cargo_before


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_not_routed_table_opens_destination_and_deadline_dialogs(client):
    call_command('seed_sample_data')

    response = client.get('/admin/dashboard/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'href="/admin/cargo/DEF789/destination/"' in content
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in content
    assert 'href="/admin/cargo/DEF789/deadline/"' in content
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in content
    assert 'hx-target="#booking-dialog"' in content
    assert 'id="booking-dialog"' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_direct_dialog_link_renders_a_dashboard_page_without_htmx(client):
    call_command('seed_sample_data')

    response = client.get('/admin/cargo/DEF789/destination/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Cargo Dashboard' in content
    assert 'role="dialog"' in content
    assert 'Change destination' in content
