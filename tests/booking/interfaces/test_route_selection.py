from datetime import UTC, datetime, timedelta

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.routing import CargoRouting
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.booking.interfaces.route_selection.views import create_route_selection_views
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository
from cargotracker.pathfinder.domain.transit_edge import TransitEdge
from cargotracker.pathfinder.domain.transit_path import TransitPath
from cargotracker.voyage.infrastructure.repository import DjangoVoyageRepository

NOW = datetime(2026, 11, 7, tzinfo=UTC)


class CandidateRoutingService:
    def __init__(self):
        self.candidates = ()

    def find_shortest_paths(self, origin, destination):
        return self.candidates


candidate_routing_service = CandidateRoutingService()
cargo_repository = DjangoCargoRepository()
dashboard = CargoDashboard(cargo_repository)
routing = CargoRouting(
    cargo_repository,
    DjangoLocationRepository(),
    DjangoVoyageRepository(),
    DjangoHandlingEventRepository(),
    candidate_routing_service,
)
route_view, select_itinerary_view = create_route_selection_views(dashboard, routing)
_, cargo_details_view = create_booking_views(dashboard)
urlpatterns = [
    path('admin/cargo/<str:tracking_id>/route/', route_view),
    path('admin/cargo/<str:tracking_id>/itineraries/', select_itinerary_view),
    path('admin/cargo/<str:tracking_id>/', cargo_details_view),
]


@pytest.fixture(autouse=True)
def reset_routing_candidates():
    candidate_routing_service.candidates = ()


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
                _edge('0100S', 'CNHKG', 'NLRTM', 1, 2),
                _edge('0200T', 'NLRTM', 'AUMEL', 3, 4),
            )
        ),
        TransitPath((_edge('0300A', 'CNHKG', 'AUMEL', 5, 6),)),
    )


@pytest.fixture
def seeded_cargo(monkeypatch):
    from cargotracker.cargo.management.commands import seed_sample_data

    monkeypatch.setattr(seed_sample_data.timezone, 'now', lambda: NOW)
    call_command('seed_sample_data')


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_and_select_itinerary_render_candidate_properties(client, seeded_cargo):
    candidate_routing_service.candidates = _candidate_paths()

    route_response = client.get('/admin/cargo/DEF789/route/')
    select_response = client.get('/admin/cargo/DEF789/itineraries/')
    route_content = route_response.content.decode()
    select_content = select_response.content.decode()

    assert route_response.status_code == 200
    assert select_response.status_code == 200
    for content in (route_content, select_content):
        assert 'Routing Details for Cargo DEF789' in content
        assert 'Hong Kong (CNHKG)' in content
        assert 'Melbourne (AUMEL)' in content
        assert '2 candidate routes' in content
        assert 'Itinerary 1' in content
        assert 'Leg 1' in content
        assert '0100S' in content
        assert 'Rotterdam (NLRTM)' in content
        assert 'Itinerary 2' in content
        assert '0300A' in content
        assert 'No routes found' not in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_and_select_itinerary_show_empty_candidate_guidance(client, seeded_cargo):
    route_response = client.get('/admin/cargo/DEF789/route/')
    select_response = client.get('/admin/cargo/DEF789/itineraries/')

    assert route_response.status_code == 200
    assert select_response.status_code == 200
    for response in (route_response, select_response):
        content = response.content.decode()
        assert 'No routes found' in content
        assert 'arrival deadline' in content
        assert 'candidate routes' not in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_assigning_candidate_redirects_to_details_with_selected_itinerary(client, seeded_cargo):
    candidate_routing_service.candidates = _candidate_paths()

    response = client.post(
        '/admin/cargo/DEF789/route/',
        {'candidate_index': '1'},
    )

    assert response.status_code == 302
    assert response['Location'] == '/admin/cargo/DEF789/'

    details_response = client.get(response['Location'])
    details_content = details_response.content.decode()
    assert details_response.status_code == 200
    assert 'Routing Details for Cargo DEF789' in details_content
    assert 'Itinerary' in details_content
    assert '0300A' in details_content
    assert '0100S' not in details_content
    assert 'Not routed' not in details_content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_invalid_candidate_selection_does_not_assign_a_route(client, seeded_cargo):
    candidate_routing_service.candidates = _candidate_paths()

    response = client.post(
        '/admin/cargo/DEF789/route/',
        {'candidate_index': '2'},
    )

    assert response.status_code == 200
    assert 'Select a valid itinerary' in response.content.decode()

    details_response = client.get('/admin/cargo/DEF789/')
    assert '<strong>Not routed</strong>' in details_response.content.decode()
