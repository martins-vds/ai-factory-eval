from dataclasses import replace

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.urls import path

from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository


class CargoRepository:
    def __init__(self):
        self._repository = DjangoCargoRepository()
        self.missing_tracking_ids = set()
        self.cargo_overrides = {}

    def find(self, tracking_id):
        if tracking_id.value in self.missing_tracking_ids:
            return None
        return self.cargo_overrides.get(tracking_id.value) or self._repository.find(tracking_id)

    def find_all(self):
        return self._repository.find_all()


repository = CargoRepository()
_, cargo_details_view = create_booking_views(repository)
urlpatterns = [path('admin/cargo/<str:tracking_id>/', cargo_details_view)]


@pytest.fixture(autouse=True)
def reset_repository():
    repository.missing_tracking_ids.clear()
    repository.cargo_overrides.clear()


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
def test_unrouted_cargo_details_link_back_to_route_action(client):
    call_command('seed_sample_data')

    response = client.get('/admin/cargo/DEF789/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Not routed' in content
    assert 'href="/admin/cargo/DEF789/route/"' in content
    assert 'route this cargo' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_misdirected_cargo_details_offer_reroute_action(client):
    call_command('seed_sample_data')
    tracking_id = TrackingId('ABC123')
    cargo = repository.find(tracking_id)
    assert cargo is not None
    repository.cargo_overrides[tracking_id.value] = replace(
        cargo, delivery=replace(cargo.delivery, misdirected=True)
    )

    response = client.get('/admin/cargo/ABC123/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Misrouted cargo!' in content
    assert 'href="/admin/cargo/ABC123/itineraries/"' in content
    assert 'Reroute' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_unknown_and_stale_cargo_details_return_http_404(client):
    call_command('seed_sample_data')
    repository.missing_tracking_ids.add('MNO456')

    unknown_response = client.get('/admin/cargo/UNKNOWN/')
    stale_response = client.get('/admin/cargo/MNO456/')

    assert unknown_response.status_code == 404
    assert stale_response.status_code == 404


@pytest.mark.parametrize(('tracking_id', 'stale'), [('UNKNOWN', False), ('MNO456', True)])
@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_unknown_and_stale_cargo_details_show_not_found_message(client, tracking_id, stale):
    call_command('seed_sample_data')
    if stale:
        repository.missing_tracking_ids.add(tracking_id)

    response = client.get(f'/admin/cargo/{tracking_id}/')

    assert response.status_code == 404
    assert f'Cargo with tracking ID {tracking_id} not found.'.encode() in response.content
