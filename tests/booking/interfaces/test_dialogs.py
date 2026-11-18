import re

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.booking.interfaces.dialogs.views import create_destination_dialog_view
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository

cargo_repository = DjangoCargoRepository()
dashboard_view, _ = create_booking_views(CargoDashboard(cargo_repository))
shipping_locations = []
destination_dialog_view = create_destination_dialog_view(
    CargoDashboard(cargo_repository),
    CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
    lambda: shipping_locations,
)
urlpatterns = [
    path('admin/dashboard/', dashboard_view),
    path('admin/cargo/<str:tracking_id>/destination/', destination_dialog_view),
]


@pytest.fixture(autouse=True)
def seed_booking_data():
    call_command('seed_sample_data')
    shipping_locations[:] = DjangoLocationRepository().find_all()
    yield
    shipping_locations.clear()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_not_routed_cargo_opens_destination_and_deadline_dialogs(client):
    response = client.get('/admin/dashboard/')
    content = response.content.decode()
    not_routed_table = content.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]

    assert response.status_code == 200
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in not_routed_table
    assert '<dialog' in not_routed_table
    assert 'id="cargo-edit-dialog"' in not_routed_table
    assert 'hx-on::after-swap=' in not_routed_table


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_excludes_origin_and_current_destination_without_mutating_locations(
    client,
):
    original_locations = tuple(location.unlocode.value for location in shipping_locations)

    response = client.get('/admin/cargo/DEF789/destination/')
    first_content = response.content.decode()
    first_options = re.findall(r'<option\b[^>]*value="([^"]+)"', first_content)
    second_content = client.get('/admin/cargo/DEF789/destination/').content.decode()
    second_options = re.findall(r'<option\b[^>]*value="([^"]+)"', second_content)

    assert response.status_code == 200
    assert 'Hong Kong' in first_content
    assert 'Melbourne' in first_content
    assert 'CNHKG' not in first_options
    assert 'AUMEL' not in first_options
    assert first_options == second_options
    assert tuple(location.unlocode.value for location in shipping_locations) == original_locations
