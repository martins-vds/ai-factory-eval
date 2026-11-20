import re
from datetime import timedelta

import pytest
from django.core import signing
from django.core.management import call_command
from django.http import Http404
from django.test import RequestFactory, override_settings
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
def test_route_page_displays_cargo_details_candidate_count_and_numbered_legs(client, monkeypatch):
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
    assert 'Route Cargo for Cargo DEF789' in content
    assert cargo.route_specification.origin.name in content
    assert cargo.route_specification.destination.name in content
    assert cargo.route_specification.arrival_deadline.strftime('%m/%d/%Y') in content
    assert 'Potential routes: 2' in content
    assert 'Route 1' in content and 'Route 2' in content
    assert 'Leg 1' in content and 'Leg 2' in content
    assert '0100S' in content and '0200T' in content
    assert '0300A' in content and '0400S' in content
    for candidate in candidates:
        for leg in candidate.legs:
            assert leg.load_location.name in content
            assert leg.load_location.unlocode.value in content
            assert leg.load_time.strftime('%m/%d/%Y') in content
            assert leg.unload_location.name in content
            assert leg.unload_location.unlocode.value in content
            assert leg.unload_time.strftime('%m/%d/%Y') in content


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
    assert 'Select Itinerary for Cargo DEF789' in content
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
def test_candidate_assignment_redirects_to_details_and_persists_itinerary(client, monkeypatch):
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


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_invalid_candidate_token_renders_an_error_response(client):
    call_command('seed_sample_data')

    response = client.post(
        '/admin/cargo/DEF789/route/',
        {'itinerary_token': 'not-a-signed-itinerary'},
    )

    assert response.status_code == 400
    assert 'Select a route shown on this page.' in response.content.decode()
    assert 'Try setting an arrival deadline further into the future.' in response.content.decode()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_candidate_token_cannot_assign_itinerary_to_another_cargo(client, monkeypatch):
    call_command('seed_sample_data')
    cargo = repository.find(TrackingId('DEF789'))
    assert cargo is not None
    candidate = _itinerary(cargo, ('0100S', '0200T'))
    monkeypatch.setattr(routing, 'route_candidates', lambda tracking_id: (candidate,))

    page = client.get('/admin/cargo/DEF789/route/')
    token = re.search(r'name="itinerary_token" value="([^"]+)"', page.content.decode())
    assert token is not None

    response = client.post(
        '/admin/cargo/MNO456/route/',
        {'itinerary_token': token.group(1)},
    )

    assert response.status_code == 400
    assert 'Select a route shown on this page.' in response.content.decode()
    assert repository.find(TrackingId('MNO456')).itinerary.legs


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_signed_empty_itinerary_is_rejected(client):
    call_command('seed_sample_data')
    token = signing.dumps(
        {'tracking_id': 'DEF789', 'legs': []},
        salt='cargotracker.booking.route-selection',
    )

    response = client.post(
        '/admin/cargo/DEF789/route/',
        {'itinerary_token': token},
    )

    assert response.status_code == 400
    assert 'Select a route shown on this page.' in response.content.decode()


@pytest.mark.django_db
def test_unknown_cargo_route_selection_raises_not_found():
    call_command('seed_sample_data')

    with pytest.raises(Http404, match=r'^Cargo with tracking ID UNKNOWN not found\.$'):
        route_selection_view(
            RequestFactory().get('/admin/cargo/UNKNOWN/route/'),
            'UNKNOWN',
        )
