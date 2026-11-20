import pytest
from django.core.management import call_command
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository

cargo_repository = DjangoCargoRepository()
dashboard_view, _ = create_booking_views(CargoDashboard(cargo_repository))

urlpatterns = [path('admin/dashboard/', dashboard_view)]


@pytest.fixture(autouse=True)
def seed_data(settings):
    settings.ROOT_URLCONF = __name__
    call_command('seed_sample_data')


@pytest.mark.django_db
def test_not_routed_table_opens_destination_and_deadline_dialogs(client):
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None

    response = client.get('/admin/dashboard/')
    not_routed_table = (
        response.content.decode().split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]
    )

    assert response.status_code == 200
    assert f'hx-get="/admin/cargo/{cargo.tracking_id.value}/destination/"' in not_routed_table
    assert f'hx-get="/admin/cargo/{cargo.tracking_id.value}/deadline/"' in not_routed_table
    assert f'href="/admin/cargo/{cargo.tracking_id.value}/route/"' in not_routed_table
    assert 'id="cargo-edit-dialog"' in not_routed_table
