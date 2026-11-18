import re
from datetime import datetime

import pytest
from django.core.management import call_command
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
shipping_locations = []
cargo_dashboard = CargoDashboard(cargo_repository)
destination_dialog, deadline_dialog = create_booking_dialog_views(
    cargo_dashboard,
    CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
    lambda: shipping_locations,
)
dashboard_view, _ = create_booking_views(cargo_dashboard)
urlpatterns = [
    path('admin/dashboard/', dashboard_view),
    path('admin/cargo/<str:tracking_id>/destination/', destination_dialog),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_dialog),
]


@pytest.fixture
def sample_booking_data():
    call_command('seed_sample_data')
    shipping_locations[:] = location_repository.find_all()
    return cargo_repository.find(TrackingId('DEF789'))


@pytest.mark.django_db
def test_not_routed_table_opens_destination_and_deadline_dialogs(client, sample_booking_data):
    response = client.get('/admin/dashboard/')
    content = response.content.decode()
    not_routed_table = content.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]

    assert response.status_code == 200
    assert 'data-tracking-id="DEF789"' in not_routed_table
    assert 'Change destination' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in not_routed_table
    assert 'Change deadline' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in not_routed_table
    assert '<dialog id="cargo-edit-dialog"' in content


@pytest.mark.django_db
def test_destination_dialog_shows_current_values_and_stable_filtered_options(
    client, sample_booking_data
):
    cargo = sample_booking_data
    assert cargo is not None
    original_locations = shipping_locations.copy()

    first = client.get('/admin/cargo/DEF789/destination/')
    second = client.get('/admin/cargo/DEF789/destination/')
    content = first.content.decode()
    options = re.search(r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', content, re.DOTALL)
    assert options is not None
    option_codes = re.findall(r'<option\b[^>]*value="([^"]+)"', options.group(1))

    assert first.status_code == second.status_code == 200
    assert cargo.route_specification.origin.name in content
    assert cargo.route_specification.destination.name in content
    assert cargo.route_specification.destination.unlocode.value not in option_codes
    assert cargo.route_specification.origin.unlocode.value not in option_codes
    assert option_codes
    assert shipping_locations == original_locations
    assert first.content == second.content


@pytest.mark.django_db
def test_destination_update_redirects_and_refreshes_the_not_routed_row(
    client, sample_booking_data
):
    cargo = sample_booking_data
    assert cargo is not None
    destination = next(
        location
        for location in shipping_locations
        if location.unlocode
        not in {
            cargo.route_specification.origin.unlocode,
            cargo.route_specification.destination.unlocode,
        }
    )
    original_origin = cargo.route_specification.origin
    original_deadline = cargo.route_specification.arrival_deadline

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'action': 'update', 'destination': destination.unlocode.value},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert response.headers['HX-Redirect'] == '/admin/dashboard/'
    refreshed = client.get('/admin/dashboard/').content.decode()
    not_routed_table = refreshed.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]

    assert destination.name in not_routed_table
    assert original_origin.name in not_routed_table
    assert original_deadline.strftime('%m/%d/%Y') in not_routed_table


@pytest.mark.django_db
def test_deadline_dialog_shows_initial_value_and_parse_error(client, sample_booking_data):
    cargo = sample_booking_data
    assert cargo is not None
    original_deadline = cargo.route_specification.arrival_deadline

    initial = client.get('/admin/cargo/DEF789/deadline/')
    invalid = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'action': 'update', 'deadline': 'not-a-date'},
        HTTP_HX_REQUEST='true',
    )
    refreshed_cargo = cargo_repository.find(TrackingId('DEF789'))

    assert initial.status_code == invalid.status_code == 200
    assert f'value="{original_deadline.date().isoformat()}"' in initial.content.decode()
    assert 'Enter a valid arrival deadline.' in invalid.content.decode()
    assert 'aria-invalid="true"' in invalid.content.decode()
    assert refreshed_cargo is not None
    assert refreshed_cargo.route_specification.arrival_deadline == original_deadline


@pytest.mark.django_db
def test_deadline_update_redirects_and_refreshes_the_not_routed_row(
    client, sample_booking_data
):
    cargo = sample_booking_data
    assert cargo is not None
    original_origin = cargo.route_specification.origin
    original_destination = cargo.route_specification.destination
    updated_deadline = datetime(2030, 1, 2, tzinfo=cargo.route_specification.arrival_deadline.tzinfo)

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'action': 'update', 'deadline': updated_deadline.date().isoformat()},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert response.headers['HX-Redirect'] == '/admin/dashboard/'
    refreshed = client.get('/admin/dashboard/').content.decode()
    not_routed_table = refreshed.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]

    assert original_origin.name in not_routed_table
    assert original_destination.name in not_routed_table
    assert updated_deadline.strftime('%m/%d/%Y') in not_routed_table
    assert 'Warning' not in response.content.decode()
