import pytest
from django.core.management import call_command
from django.http import Http404
from django.test import RequestFactory, override_settings
from django.urls import path

from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository


class CargoRepository:
    def __init__(self):
        self._repository = DjangoCargoRepository()
        self.missing_tracking_ids = set()

    def find(self, tracking_id):
        if tracking_id.value in self.missing_tracking_ids:
            return None
        return self._repository.find(tracking_id)

    def find_all(self):
        return self._repository.find_all()


repository = CargoRepository()
_, cargo_details_view = create_booking_views(repository)
urlpatterns = [path('admin/cargo/<str:tracking_id>/', cargo_details_view)]


@pytest.fixture(autouse=True)
def reset_repository():
    repository.missing_tracking_ids.clear()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_cargo_details_render_route_fields_and_itinerary(client):
    call_command('seed_sample_data')

    response = client.get('/admin/cargo/MNO456/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Routing Details for Cargo MNO456' in content
    assert 'Origin:' in content
    assert 'New York' in content
    assert 'USNYC' in content
    assert 'Destination:' in content
    assert 'Dallas' in content
    assert 'USDAL' in content
    assert 'Arrival deadline:' in content
    assert 'Itinerary' in content
    assert '0200T' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_cargo_details_render_routing_state_actions(client):
    call_command('seed_sample_data')

    unrouted_response = client.get('/admin/cargo/DEF789/')
    unrouted_content = unrouted_response.content.decode()
    misrouted_response = client.get('/admin/cargo/JKL567/')
    misrouted_content = misrouted_response.content.decode()
    on_track_response = client.get('/admin/cargo/ABC123/')
    on_track_content = on_track_response.content.decode()

    assert unrouted_response.status_code == 200
    assert 'Not routed' in unrouted_content
    assert 'href="/admin/cargo/DEF789/route/"' in unrouted_content
    assert misrouted_response.status_code == 200
    assert 'Misrouted cargo!' in misrouted_content
    assert 'href="/admin/cargo/JKL567/itineraries/"' in misrouted_content
    assert on_track_response.status_code == 200
    assert 'Misrouted cargo!' not in on_track_content
    assert '/itineraries/' not in on_track_content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_unknown_and_stale_cargo_details_return_http_404(client):
    call_command('seed_sample_data')
    repository.missing_tracking_ids.add('MNO456')

    unknown_response = client.get('/admin/cargo/UNKNOWN/')
    stale_response = client.get('/admin/cargo/MNO456/')

    assert unknown_response.status_code == 404
    assert stale_response.status_code == 404
    for tracking_id in ('UNKNOWN', 'MNO456'):
        with pytest.raises(
            Http404,
            match=rf'^Cargo with tracking ID {tracking_id} not found\.$',
        ):
            cargo_details_view(
                RequestFactory().get(f'/admin/cargo/{tracking_id}/'),
                tracking_id,
            )
