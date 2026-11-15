import re
from datetime import UTC, datetime

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
cargo_dashboard = CargoDashboard(cargo_repository)
location_repository = DjangoLocationRepository()
specification = CargoSpecification(cargo_repository, DjangoHandlingEventRepository())
destination_view, deadline_view = create_booking_dialog_views(
    specification, cargo_dashboard, location_repository.find_all
)
dashboard_view, _ = create_booking_views(cargo_dashboard)
urlpatterns = [
    path('admin/dashboard/', dashboard_view),
    path('admin/cargo/<str:tracking_id>/destination/', destination_view),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_view),
]


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_not_routed_table_opens_edit_dialogs_without_changing_its_route_link(client):
    call_command('seed_sample_data')

    response = client.get('/admin/dashboard/')
    content = response.content.decode()
    not_routed_table = content.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]

    assert response.status_code == 200
    assert 'href="/admin/cargo/DEF789/route/"' in not_routed_table
    assert 'href="/admin/cargo/DEF789/destination/"' in not_routed_table
    assert 'href="/admin/cargo/DEF789/deadline/"' in not_routed_table
    assert 'id="booking-dialog-content"' in content
    assert re.findall(r'data-tracking-id="([^"]+)"', not_routed_table) == ['DEF789']


@pytest.mark.django_db
def test_destination_dialog_shows_current_values_and_stable_filtered_options():
    call_command('seed_sample_data')
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    locations = location_repository.find_all()
    original_locations = list(locations)
    view, _ = create_booking_dialog_views(specification, cargo_dashboard, lambda: locations)
    request = RequestFactory().get('/admin/cargo/DEF789/destination/', HTTP_HX_REQUEST='true')

    first_content = view(request, 'DEF789').content.decode()
    second_content = view(request, 'DEF789').content.decode()
    options = re.search(
        r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', first_content, re.DOTALL
    )
    second_options = re.search(
        r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', second_content, re.DOTALL
    )

    assert options is not None
    assert cargo.route_specification.origin.name in first_content
    assert cargo.route_specification.destination.name in first_content
    assert cargo.route_specification.destination.unlocode.value in first_content
    assert cargo.route_specification.origin.unlocode.value not in options.group(1)
    assert cargo.route_specification.destination.unlocode.value not in options.group(1)
    assert second_options is not None
    assert options.group(1) == second_options.group(1)
    assert locations == original_locations
    assert 'Cancel' in first_content
    assert 'Update' in first_content


@pytest.mark.django_db
def test_deadline_dialog_reports_invalid_dates_without_losing_the_current_value():
    call_command('seed_sample_data')
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    view = deadline_view
    get_request = RequestFactory().get('/admin/cargo/DEF789/deadline/', HTTP_HX_REQUEST='true')
    post_request = RequestFactory().post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': 'not-a-date'},
        HTTP_HX_REQUEST='true',
    )

    initial_content = view(get_request, 'DEF789').content.decode()
    error_content = view(post_request, 'DEF789').content.decode()

    assert cargo.route_specification.origin.name in initial_content
    assert cargo.route_specification.destination.name in initial_content
    assert cargo.route_specification.arrival_deadline.date().isoformat() in initial_content
    assert 'Enter a valid arrival deadline.' in error_content
    assert 'aria-invalid="true"' in error_content
    assert 'not-a-date' in error_content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_update_preserves_other_specification_fields_and_refreshes_dashboard(client):
    call_command('seed_sample_data')
    original = cargo_repository.find(TrackingId('DEF789'))
    assert original is not None

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'FIHEL'},
        follow=True,
    )
    updated = cargo_repository.find(TrackingId('DEF789'))
    content = response.content.decode()

    assert response.redirect_chain == [('/admin/dashboard/', 302)]
    assert updated is not None
    assert updated.route_specification.origin == original.route_specification.origin
    assert (
        updated.route_specification.arrival_deadline
        == original.route_specification.arrival_deadline
    )
    assert updated.route_specification.destination.unlocode.value == 'FIHEL'
    assert 'Helsinki' in content
    assert 'Unavailable widget' not in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_update_preserves_other_specification_fields_and_completes_htmx_dialog(client):
    call_command('seed_sample_data')
    original = cargo_repository.find(TrackingId('DEF789'))
    assert original is not None
    deadline = datetime(2031, 3, 5, tzinfo=UTC)

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': deadline.date().isoformat()},
        HTTP_HX_REQUEST='true',
    )
    updated = cargo_repository.find(TrackingId('DEF789'))
    refreshed_dashboard = client.get('/admin/dashboard/').content.decode()

    assert response.status_code == 204
    assert response.headers['HX-Redirect'] == '/admin/dashboard/'
    assert updated is not None
    assert updated.route_specification.origin == original.route_specification.origin
    assert updated.route_specification.destination == original.route_specification.destination
    assert updated.route_specification.arrival_deadline == deadline
    assert '03/05/2031' in refreshed_dashboard
    assert 'Unavailable widget' not in refreshed_dashboard
