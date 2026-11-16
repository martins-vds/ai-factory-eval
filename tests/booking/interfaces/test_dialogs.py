import re
from datetime import datetime

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
from cargotracker.location.domain.un_locode import UnLocode
from cargotracker.location.infrastructure.repository import DjangoLocationRepository

cargo_repository = DjangoCargoRepository()
cargo_dashboard = CargoDashboard(cargo_repository)
cargo_specification = CargoSpecification(
    cargo_repository,
    DjangoHandlingEventRepository(),
)


def _shipping_locations():
    return DjangoLocationRepository().find_all()


dashboard_view, _ = create_booking_views(cargo_dashboard)
destination_dialog_view, deadline_dialog_view = create_booking_dialog_views(
    cargo_dashboard,
    cargo_specification,
    _shipping_locations,
)
urlpatterns = [
    path('admin/dashboard/', dashboard_view),
    path('admin/cargo/<str:tracking_id>/destination/', destination_dialog_view),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_dialog_view),
]


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_not_routed_table_opens_accessible_destination_and_deadline_dialogs(client):
    call_command('seed_sample_data')

    content = client.get('/admin/dashboard/').content.decode()
    not_routed_table = content.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]

    assert 'id="cargo-edit-dialog"' in not_routed_table
    assert 'aria-haspopup="dialog"' in not_routed_table
    assert 'aria-label="Change destination for cargo DEF789"' in not_routed_table
    assert 'href="/admin/cargo/DEF789/destination/"' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in not_routed_table
    assert 'aria-label="Change deadline for cargo DEF789"' in not_routed_table
    assert 'href="/admin/cargo/DEF789/deadline/"' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in not_routed_table
    assert 'href="/admin/cargo/DEF789/route/"' in not_routed_table


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_shows_current_route_and_filters_options_without_mutation(
    client, monkeypatch
):
    call_command('seed_sample_data')
    locations = DjangoLocationRepository().find_all()
    original_locations = locations.copy()
    monkeypatch.setattr(DjangoLocationRepository, 'find_all', lambda self: locations)

    first = client.get('/admin/cargo/DEF789/destination/')
    second = client.get('/admin/cargo/DEF789/destination/')
    content = first.content.decode()
    options = re.findall(r'<option value="([^"]+)"', content)
    second_options = re.findall(r'<option value="([^"]+)"', second.content.decode())

    assert first.status_code == 200
    assert 'Hong Kong (CNHKG)' in content
    assert 'Melbourne (AUMEL)' in content
    assert options == second_options
    assert 'CNHKG' not in options
    assert 'AUMEL' not in options
    assert 'USNYC' in options
    assert locations == original_locations


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_shows_current_deadline_and_reports_invalid_input(client):
    call_command('seed_sample_data')

    response = client.get('/admin/cargo/DEF789/deadline/')
    content = response.content.decode()
    assert re.search(r'name="deadline"[^>]*value="\d{4}-\d{2}-\d{2}"', content)

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': 'not-a-date', 'action': 'update'},
        HTTP_HX_REQUEST='true',
    )
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Enter a valid arrival deadline.' in content
    assert 'id="deadline-error"' in content
    assert 'aria-invalid="true"' in content
    assert 'value="not-a-date"' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_update_completes_dialog_and_refreshes_not_routed_row(client):
    call_command('seed_sample_data')
    original = cargo_repository.find(TrackingId('DEF789'))
    assert original is not None

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'USNYC', 'action': 'update'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert response['HX-Redirect'] == '/admin/dashboard/'
    assert b'console.warn' not in response.content

    updated = cargo_repository.find(TrackingId('DEF789'))
    assert updated is not None
    assert updated.route_specification.origin == original.route_specification.origin
    assert updated.route_specification.destination == DjangoLocationRepository().find(
        UnLocode('USNYC')
    )
    assert updated.route_specification.arrival_deadline == original.route_specification.arrival_deadline

    refreshed = client.get('/admin/dashboard/').content.decode()
    not_routed_table = refreshed.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]
    assert 'New York' in not_routed_table
    assert 'USNYC' in not_routed_table
    assert 'data-tracking-id="DEF789"' in not_routed_table


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_update_keeps_other_route_fields_and_redirects_to_refreshed_dashboard(client):
    call_command('seed_sample_data')
    original = cargo_repository.find(TrackingId('DEF789'))
    assert original is not None

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': '2030-11-20', 'action': 'update'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert response['HX-Redirect'] == '/admin/dashboard/'
    assert b'console.warn' not in response.content

    updated = cargo_repository.find(TrackingId('DEF789'))
    assert updated is not None
    assert updated.route_specification.origin == original.route_specification.origin
    assert updated.route_specification.destination == original.route_specification.destination
    assert updated.route_specification.arrival_deadline.date() == datetime(2030, 11, 20).date()

    refreshed = client.get('/admin/dashboard/').content.decode()
    not_routed_table = refreshed.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]
    assert '11/20/2030' in not_routed_table
