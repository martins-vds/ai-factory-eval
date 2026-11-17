from django.core.management import call_command
from django.test import override_settings
from django.urls import path
import pytest

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository


dashboard_view, _ = create_booking_views(CargoDashboard(DjangoCargoRepository()))
urlpatterns = [path('admin/dashboard/', dashboard_view)]


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_dashboard_opens_destination_and_deadline_dialogs_from_not_routed_rows(client):
    call_command('seed_sample_data')

    response = client.get('/admin/dashboard/')
    content = response.content.decode()
    not_routed_table = content.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]

    assert response.status_code == 200
    assert 'data-tracking-id="DEF789"' in not_routed_table
    assert 'Hong Kong' in not_routed_table and 'Melbourne' in not_routed_table
    assert 'href="/admin/cargo/DEF789/route/"' in not_routed_table
    assert 'href="/admin/cargo/DEF789/destination/"' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in not_routed_table
    assert 'href="/admin/cargo/DEF789/deadline/"' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in not_routed_table
    assert 'id="cargo-edit-dialog"' in content
