import random
from datetime import UTC, datetime

import pytest
from django.core.management import call_command
from django.test import RequestFactory, override_settings
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.registration import CargoRegistration
from cargotracker.booking.application.routing import CargoRouting
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.booking.interfaces.route_selection import views as route_selection_views
from cargotracker.booking.interfaces.route_selection.views import (
    create_route_selection_views,
)
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.domain.un_locode import UnLocode
from cargotracker.location.infrastructure.repository import DjangoLocationRepository
from cargotracker.pathfinder.application.routing import RoutingService
from cargotracker.voyage.infrastructure.repository import DjangoVoyageRepository

ORIGIN = UnLocode('USNYC')
DESTINATION = UnLocode('USDAL')
ROUTE_TIME = datetime(2026, 11, 7, tzinfo=UTC)
DEADLINE = datetime(2030, 11, 5, tzinfo=UTC)
SHORT_DEADLINE = datetime(2026, 11, 8, tzinfo=UTC)

cargo_repository = DjangoCargoRepository()
location_repository = DjangoLocationRepository()
voyage_repository = DjangoVoyageRepository()
cargo_dashboard = CargoDashboard(cargo_repository)
cargo_routing = CargoRouting(
    cargo_repository,
    location_repository,
    voyage_repository,
    DjangoHandlingEventRepository(),
    RoutingService(random.Random(42), lambda: ROUTE_TIME),
)
route_view, select_itinerary_view = create_route_selection_views(
    cargo_routing,
    cargo_dashboard,
)
_, cargo_details_view = create_booking_views(cargo_dashboard)
urlpatterns = [
    path('admin/cargo/<str:tracking_id>/route/', route_view),
    path('admin/cargo/<str:tracking_id>/itineraries/', select_itinerary_view),
    path('admin/cargo/<str:tracking_id>/', cargo_details_view, name='cargo-details'),
]


def _register_cargo(deadline=DEADLINE):
    call_command('seed_sample_data')
    origin = location_repository.find(ORIGIN)
    destination = location_repository.find(DESTINATION)
    assert origin is not None
    assert destination is not None
    return CargoRegistration(cargo_repository).register(origin, destination, deadline)


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_screen_shows_details_and_valid_candidate_itinerary_legs(client):
    tracking_id = _register_cargo()

    response = client.get(f'/admin/cargo/{tracking_id.value}/route/')

    assert response.status_code == 200
    content = response.content.decode()
    candidates = response.context['candidates']
    cargo = cargo_repository.find(tracking_id)
    assert cargo is not None
    assert candidates
    assert response.context['candidate_count'] == len(candidates)
    assert f'Routing Details for Cargo {tracking_id.value}' in content
    assert cargo.route_specification.origin.name in content
    assert cargo.route_specification.destination.name in content
    assert f'Potential routes: {len(candidates)}' in content

    for candidate_number, candidate in enumerate(candidates, 1):
        itinerary = candidate['itinerary']
        assert itinerary.legs
        assert itinerary.legs[0].load_location == cargo.route_specification.origin
        assert itinerary.legs[-1].unload_location == cargo.route_specification.destination
        assert all(
            first.unload_location == second.load_location
            for first, second in zip(itinerary.legs, itinerary.legs[1:])
        )
        assert f'Candidate {candidate_number}' in content
        for leg_number, leg in enumerate(itinerary.legs, 1):
            assert f'Leg {leg_number}' in content
            assert leg.voyage.voyage_number.value in content
            assert leg.load_location.name in content
            assert leg.unload_location.name in content
            assert leg.load_time.strftime('%m/%d/%Y') in content
            assert leg.unload_time.strftime('%m/%d/%Y') in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_select_itinerary_screen_renders_candidates_when_present(client):
    tracking_id = _register_cargo()

    response = client.get(f'/admin/cargo/{tracking_id.value}/itineraries/')

    assert response.status_code == 200
    assert response.context['candidates']
    assert 'Candidate 1' in response.content.decode()
    assert 'No routes found that satisfy the route specification.' not in response.content.decode()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_select_itinerary_screen_guides_when_no_candidates_exist(client):
    tracking_id = _register_cargo(SHORT_DEADLINE)

    response = client.get(f'/admin/cargo/{tracking_id.value}/itineraries/')
    content = response.content.decode()

    assert response.status_code == 200
    assert response.context['candidates'] == []
    assert 'No routes found that satisfy the route specification.' in content
    assert 'Try setting an arrival deadline further into the future' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_assigning_candidate_redirects_to_details_and_shows_persisted_itinerary(client):
    tracking_id = _register_cargo()
    route_url = f'/admin/cargo/{tracking_id.value}/route/'
    route_response = client.get(route_url)
    candidate = route_response.context['candidates'][0]

    assignment_response = client.post(
        route_url,
        {'candidate_token': candidate['token']},
    )

    details_url = f'/admin/cargo/{tracking_id.value}/'
    assert assignment_response.status_code == 302
    assert assignment_response['Location'] == details_url
    details_response = client.get(assignment_response['Location'])
    persisted_cargo = cargo_repository.find(TrackingId(tracking_id.value))
    assert details_response.status_code == 200
    assert 'Itinerary' in details_response.content.decode()
    assert persisted_cargo is not None and persisted_cargo.itinerary == candidate['itinerary']
    assert (
        candidate['itinerary'].legs[0].voyage.voyage_number.value
        in details_response.content.decode()
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_selection_rejects_tampered_and_cross_cargo_candidate_tokens(client):
    source_tracking_id = _register_cargo()
    target_tracking_id = _register_cargo()
    source_response = client.get(f'/admin/cargo/{source_tracking_id.value}/route/')
    candidate_token = source_response.context['candidates'][0]['token']
    target_url = f'/admin/cargo/{target_tracking_id.value}/route/'

    tampered_response = client.post(target_url, {'candidate_token': f'{candidate_token}x'})
    cross_cargo_response = client.post(target_url, {'candidate_token': candidate_token})

    cargo = cargo_repository.find(target_tracking_id)
    assert tampered_response.status_code == 400
    assert cross_cargo_response.status_code == 400
    assert cargo is not None
    assert not cargo.itinerary.legs


@override_settings(ROOT_URLCONF=__name__)
def test_route_assignment_redirects_to_details_route(monkeypatch):
    class Dashboard:
        def get_cargo_details(self, tracking_id):
            return object()

    class Routing:
        def assign_route(self, tracking_id, itinerary):
            pass

    monkeypatch.setattr(
        route_selection_views,
        '_itinerary_from_token',
        lambda token, tracking_id: object(),
    )
    route_view, _ = create_route_selection_views(Routing(), Dashboard())

    response = route_view(
        RequestFactory().post('/admin/cargo/ABC123/route/', {'candidate_token': 'token'}),
        'ABC123',
    )

    assert response['Location'] == '/admin/cargo/ABC123/'


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_selection_form_posts_to_its_path_and_rejects_other_methods(client):
    tracking_id = _register_cargo()
    route_url = f'/admin/cargo/{tracking_id.value}/route/'

    response = client.get(route_url)
    method_not_allowed = client.put(route_url)

    assert f'action="{route_url}"' in response.content.decode()
    assert method_not_allowed.status_code == 405
    assert method_not_allowed['Allow'] == 'GET, POST'
