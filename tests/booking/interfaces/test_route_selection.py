import re
from datetime import timedelta

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.routing import CargoRouting
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.booking.interfaces.route_selection.views import create_route_selection_views
from cargotracker.cargo.domain.itinerary import Itinerary
from cargotracker.cargo.domain.leg import Leg
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.domain.un_locode import UnLocode
from cargotracker.location.infrastructure.repository import DjangoLocationRepository
from cargotracker.voyage.domain.voyage_number import VoyageNumber
from cargotracker.voyage.infrastructure.repository import DjangoVoyageRepository

repository = DjangoCargoRepository()
dashboard = CargoDashboard(repository)
routing = CargoRouting(
    repository,
    DjangoLocationRepository(),
    DjangoVoyageRepository(),
    DjangoHandlingEventRepository(),
    routing_service=None,
)
route_selection_view, select_itinerary_view = create_route_selection_views(routing, dashboard)
_, cargo_details_view = create_booking_views(dashboard)
urlpatterns = [
    path('admin/cargo/<str:tracking_id>/route/', route_selection_view),
    path('admin/cargo/<str:tracking_id>/itineraries/', select_itinerary_view),
    path('admin/cargo/<str:tracking_id>/', cargo_details_view),
]


@pytest.fixture(autouse=True)
def reset_candidates(monkeypatch):
    monkeypatch.setattr(routing, 'route_candidates', lambda tracking_id: ())


def _itinerary(cargo, voyage_numbers):
    locations = DjangoLocationRepository()
    voyages = DjangoVoyageRepository()
    transfer = locations.find(UnLocode('NLRTM'))
    assert transfer is not None
    deadline = cargo.route_specification.arrival_deadline
    return Itinerary(
        (
            Leg(
                voyages.find(VoyageNumber(voyage_numbers[0])),
                cargo.route_specification.origin,
                transfer,
                deadline - timedelta(days=4),
                deadline - timedelta(days=3),
            ),
            Leg(
                voyages.find(VoyageNumber(voyage_numbers[1])),
                transfer,
                cargo.route_specification.destination,
                deadline - timedelta(days=2),
                deadline - timedelta(days=1),
            ),
        )
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_page_displays_cargo_details_candidate_count_and_numbered_legs(
    client, monkeypatch
):
    call_command('seed_sample_data')
    cargo = repository.find(TrackingId('DEF789'))
    assert cargo is not None
    candidates = (
        _itinerary(cargo, ('0100S', '0200T')),
        _itinerary(cargo, ('0300A', '0400S')),
    )
    monkeypatch.setattr(routing, 'route_candidates', lambda tracking_id: candidates)

    response = client.get('/admin/cargo/DEF789/route/')
    content = response.content.decode()

    assert response.status_code == 200
    assert cargo.route_specification.origin.name in content
    assert cargo.route_specification.destination.name in content
    assert 'Potential routes: 2' in content
    assert 'Route 1' in content and 'Route 2' in content
    assert 'Leg 1' in content and 'Leg 2' in content
    assert '0100S' in content and '0200T' in content
    assert '0300A' in content and '0400S' in content
    assert candidates[0].legs[0].load_location.unlocode.value in content
    assert candidates[0].legs[1].unload_location.unlocode.value in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_select_itinerary_renders_populated_candidates(client, monkeypatch):
    call_command('seed_sample_data')
    cargo = repository.find(TrackingId('DEF789'))
    assert cargo is not None
    candidate = _itinerary(cargo, ('0100S', '0200T'))
    monkeypatch.setattr(routing, 'route_candidates', lambda tracking_id: (candidate,))

    response = client.get('/admin/cargo/DEF789/itineraries/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Potential routes: 1' in content
    assert 'Route 1' in content
    assert '0100S' in content and '0200T' in content
    assert 'No routes found' not in content


@pytest.mark.parametrize(
    ('path', 'message'),
    [
        (
            '/admin/cargo/DEF789/route/',
            'Try setting an arrival deadline further into the future.',
        ),
        (
            '/admin/cargo/DEF789/itineraries/',
            'Try setting an arrival deadline further into the future (a few weeks at least).',
        ),
    ],
)
@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_empty_candidates_render_the_screen_specific_guidance(client, path, message):
    call_command('seed_sample_data')

    response = client.get(path)
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Potential routes: 0' in content
    assert 'No routes found that satisfy the route specification.' in content
    assert message in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_candidate_assignment_redirects_to_details_and_persists_itinerary(
    client, monkeypatch
):
    call_command('seed_sample_data')
    cargo = repository.find(TrackingId('DEF789'))
    assert cargo is not None
    candidate = _itinerary(cargo, ('0100S', '0200T'))
    monkeypatch.setattr(routing, 'route_candidates', lambda tracking_id: (candidate,))

    page = client.get('/admin/cargo/DEF789/route/')
    token = re.search(
        r'name="itinerary_token" value="([^"]+)"',
        page.content.decode(),
    )
    assert token is not None

    response = client.post(
        '/admin/cargo/DEF789/route/',
        {'itinerary_token': token.group(1)},
        follow=True,
    )
    stored = repository.find(TrackingId('DEF789'))

    assert response.status_code == 200
    assert response.redirect_chain == [('/admin/cargo/DEF789/', 302)]
    assert 'Routing Details for Cargo DEF789' in response.content.decode()
    assert 'Itinerary' in response.content.decode()
    assert '0100S' in response.content.decode() and '0200T' in response.content.decode()
    assert stored is not None
    assert stored.itinerary == candidate
