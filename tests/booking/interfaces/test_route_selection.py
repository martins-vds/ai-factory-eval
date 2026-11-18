from datetime import UTC, datetime

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

ORIGIN = 'CNHKG'
TRANSFER = 'JNTKO'
DESTINATION = 'AUMEL'


class CandidateRoutingService:
    def __init__(self):
        self.candidates = ()
        self.requested_route = None

    def find_shortest_paths(self, origin, destination):
        self.requested_route = (origin, destination)
        return self.candidates


def _edge(voyage, from_port, to_port, departure_day, arrival_day):
    return TransitEdge(
        voyage,
        from_port,
        to_port,
        datetime(2026, 11, departure_day, tzinfo=UTC),
        datetime(2026, 11, arrival_day, tzinfo=UTC),
    )


def _candidate_paths():
    return (
        TransitPath(
            (
                _edge('0300A', ORIGIN, TRANSFER, 8, 9),
                _edge('0200T', TRANSFER, DESTINATION, 10, 11),
            )
        ),
        TransitPath(
            (
                _edge('0100S', ORIGIN, 'SESTO', 12, 13),
                _edge('0400S', 'SESTO', DESTINATION, 14, 15),
            )
        ),
    )


candidate_routing_service = CandidateRoutingService()
cargo_repository = DjangoCargoRepository()
cargo_dashboard = CargoDashboard(cargo_repository)
route_view, select_itinerary_view = create_route_selection_views(
    CargoRouting(
        cargo_repository,
        DjangoLocationRepository(),
        DjangoVoyageRepository(),
        DjangoHandlingEventRepository(),
        candidate_routing_service,
    ),
    cargo_dashboard,
)
_, cargo_details_view = create_booking_views(cargo_dashboard)
urlpatterns = [
    path('admin/cargo/<str:tracking_id>/route/', route_view),
    path('admin/cargo/<str:tracking_id>/itineraries/', select_itinerary_view),
    path('admin/cargo/<str:tracking_id>/', cargo_details_view),
]


@pytest.fixture(autouse=True)
def reset_candidate_routing():
    candidate_routing_service.candidates = ()
    candidate_routing_service.requested_route = None


@pytest.fixture
def seeded_route_candidates(monkeypatch):
    now = datetime(2026, 11, 7, tzinfo=UTC)
    monkeypatch.setattr('cargotracker.cargo.management.commands.seed_sample_data.timezone.now', lambda: now)
    call_command('seed_sample_data')
    candidate_routing_service.candidates = _candidate_paths()
    return cargo_repository.find(TrackingId('DEF789'))


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_page_displays_candidate_count_and_numbered_itinerary_legs(
    client, seeded_route_candidates
):
    response = client.get('/admin/cargo/DEF789/route/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Routing Details for Cargo DEF789' in content
    assert 'Potential routes: 2' in content
    assert 'Itinerary 1' in content and 'Itinerary 2' in content
    assert 'Leg 1' in content and 'Leg 2' in content
    assert '0300A' in content and '0200T' in content

    candidates = [route['itinerary'] for route in response.context['routes']]
    assert candidate_routing_service.requested_route == (ORIGIN, DESTINATION)
    assert candidates
    assert all(candidate.legs for candidate in candidates)
    assert all(candidate.legs[0].load_location == seeded_route_candidates.route_specification.origin for candidate in candidates)
    assert all(candidate.legs[-1].unload_location == seeded_route_candidates.route_specification.destination for candidate in candidates)
    assert all(
        first.unload_location == second.load_location
        for candidate in candidates
        for first, second in zip(candidate.legs, candidate.legs[1:])
    )
