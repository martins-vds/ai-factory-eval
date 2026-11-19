from datetime import UTC, datetime, timedelta

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.routing import CargoRouting
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.booking.interfaces.route_selection.views import create_route_selection_views
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository
from cargotracker.pathfinder.domain.transit_edge import TransitEdge
from cargotracker.pathfinder.domain.transit_path import TransitPath
from cargotracker.voyage.infrastructure.repository import DjangoVoyageRepository

NOW = datetime(2026, 11, 7, tzinfo=UTC)
NO_ROUTES_MESSAGE = (
    'No routes found that satisfy the route specification. Try setting an arrival deadline '
    'further into the future (a few weeks at least).'
)


class CandidateRoutingService:
    def __init__(self):
        self.paths = ()

    def find_shortest_paths(self, origin, destination):
        return self.paths


def _edge(voyage, from_port, to_port, departure_day, arrival_day):
    return TransitEdge(
        voyage,
        from_port,
        to_port,
        NOW + timedelta(days=departure_day),
        NOW + timedelta(days=arrival_day),
    )


def _candidate_paths():
    return (
        TransitPath(
            (
                _edge('0100S', 'CNHKG', 'JNTKO', 1, 2),
                _edge('0200T', 'JNTKO', 'AUMEL', 3, 4),
            )
        ),
        TransitPath((_edge('0300A', 'CNHKG', 'AUMEL', 5, 6),)),
    )


cargo_repository = DjangoCargoRepository()
routing_service = CandidateRoutingService()
cargo_routing = CargoRouting(
    cargo_repository,
    DjangoLocationRepository(),
    DjangoVoyageRepository(),
    DjangoHandlingEventRepository(),
    routing_service,
)
route_view, itinerary_view = create_route_selection_views(
    cargo_routing,
    CargoDashboard(cargo_repository),
)
_, cargo_details_view = create_booking_views(CargoDashboard(cargo_repository))
urlpatterns = [
    path('admin/cargo/<str:tracking_id>/', cargo_details_view),
    path('admin/cargo/<str:tracking_id>/route/', route_view),
    path('admin/cargo/<str:tracking_id>/itineraries/', itinerary_view),
]


@pytest.fixture(autouse=True)
def set_up_routes(monkeypatch):
    routing_service.paths = ()
    monkeypatch.setattr(
        'cargotracker.cargo.management.commands.seed_sample_data.timezone.now',
        lambda: NOW,
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_page_displays_cargo_details_and_candidate_itinerary_properties(client):
    call_command('seed_sample_data')
    routing_service.paths = _candidate_paths()

    response = client.get('/admin/cargo/DEF789/route/')
    content = response.content.decode()
    cargo = cargo_repository.find(TrackingId('DEF789'))
    candidates = response.context['candidates']

    assert response.status_code == 200
    assert cargo is not None
    assert 'Route Cargo DEF789' in content
    assert 'Hong Kong' in content and 'CNHKG' in content
    assert 'Melbourne' in content and 'AUMEL' in content
    assert 'Arrival deadline:' in content
    assert 'Potential routes: 2' in content
    assert 'Itinerary 1' in content and 'Itinerary 2' in content
    assert '0100S' in content and '0200T' in content and '0300A' in content
    assert len(candidates) == 2
    for candidate in candidates:
        assert candidate.legs
        assert candidate.legs[0].load_location == cargo.route_specification.origin
        assert candidate.legs[-1].unload_location == cargo.route_specification.destination
        assert all(
            first.unload_location == second.load_location
            for first, second in zip(candidate.legs, candidate.legs[1:])
        )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_itinerary_page_renders_candidates_when_present(client):
    call_command('seed_sample_data')
    routing_service.paths = _candidate_paths()

    response = client.get('/admin/cargo/DEF789/itineraries/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Select an itinerary for cargo DEF789' in content
    assert 'Potential routes: 2' in content
    assert 'Itinerary 1' in content and 'Itinerary 2' in content
    assert NO_ROUTES_MESSAGE not in content


@pytest.mark.parametrize(
    'path',
    ('route/', 'itineraries/'),
    ids=('route-page', 'itinerary-page'),
)
@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_selection_guides_the_user_when_no_candidates_exist(client, path):
    call_command('seed_sample_data')

    response = client.get(f'/admin/cargo/DEF789/{path}')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Potential routes: 0' in content
    assert NO_ROUTES_MESSAGE in content
    assert 'name="candidate_index"' not in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_assignment_persists_the_displayed_candidate_and_opens_cargo_details(client):
    call_command('seed_sample_data')
    routing_service.paths = _candidate_paths()
    route_page = client.get('/admin/cargo/DEF789/route/')
    selected_itinerary = route_page.context['candidates'][0]
    routing_service.paths = ()

    response = client.post(
        '/admin/cargo/DEF789/route/',
        {'candidate_index': '0'},
        follow=True,
    )
    content = response.content.decode()
    assigned = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 200
    assert response.redirect_chain == [('/admin/cargo/DEF789/', 302)]
    assert 'Routing Details for Cargo DEF789' in content
    assert 'Itinerary' in content
    assert '0100S' in content and '0200T' in content
    assert assigned is not None
    assert assigned.itinerary == selected_itinerary


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_invalid_candidate_selection_is_reported_without_assigning_a_route(client):
    call_command('seed_sample_data')
    routing_service.paths = _candidate_paths()
    client.get('/admin/cargo/DEF789/route/')

    response = client.post(
        '/admin/cargo/DEF789/route/',
        {'candidate_index': '2'},
    )
    cargo = cargo_repository.find(TrackingId('DEF789'))
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Select one of the available itineraries.' in content
    assert 'Potential routes: 2' in content
    assert cargo is not None
    assert not cargo.itinerary.legs
