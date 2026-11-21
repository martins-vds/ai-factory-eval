import re
from datetime import UTC, datetime, timedelta

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.urls import clear_url_caches, path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.routing import CargoRouting
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.booking.interfaces.route_selection.views import create_route_selection_views
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.cargo.management.commands import seed_sample_data
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository
from cargotracker.pathfinder.domain.transit_edge import TransitEdge
from cargotracker.pathfinder.domain.transit_path import TransitPath
from cargotracker.voyage.infrastructure.repository import DjangoVoyageRepository

urlpatterns = []


class CandidateRoutingService:
    def __init__(self, candidates):
        self.candidates = candidates
        self.request_count = 0

    def find_shortest_paths(self, origin, destination):
        self.request_count += 1
        if self.request_count == 1:
            return self.candidates
        return tuple(reversed(self.candidates))


@pytest.fixture
def booking_pages(monkeypatch):
    global urlpatterns
    tracking_id = TrackingId('DEF789')
    monkeypatch.setattr(
        seed_sample_data.timezone,
        'now',
        lambda: datetime(2026, 11, 7, tzinfo=UTC),
    )
    call_command('seed_sample_data')

    cargo_repository = DjangoCargoRepository()
    cargo = cargo_repository.find(tracking_id)
    assert cargo is not None
    deadline = cargo.route_specification.arrival_deadline
    origin = cargo.route_specification.origin.unlocode.value
    destination = cargo.route_specification.destination.unlocode.value
    transfer = 'NLRTM'
    candidates = (
        TransitPath(
            (
                TransitEdge(
                    '0200T',
                    origin,
                    transfer,
                    deadline - timedelta(days=5),
                    deadline - timedelta(days=4),
                ),
                TransitEdge(
                    '0300A',
                    transfer,
                    destination,
                    deadline - timedelta(days=3),
                    deadline - timedelta(days=2),
                ),
            )
        ),
        TransitPath(
            (
                TransitEdge(
                    '0400S',
                    origin,
                    destination,
                    deadline - timedelta(days=2),
                    deadline - timedelta(days=1),
                ),
            )
        ),
    )
    routing_service = CandidateRoutingService(candidates)
    cargo_routing = CargoRouting(
        cargo_repository,
        DjangoLocationRepository(),
        DjangoVoyageRepository(),
        DjangoHandlingEventRepository(),
        routing_service,
    )
    cargo_dashboard = CargoDashboard(cargo_repository)
    route_view, select_itinerary_view = create_route_selection_views(cargo_routing, cargo_dashboard)
    _, cargo_details_view = create_booking_views(cargo_dashboard)
    urlpatterns = [
        path('admin/cargo/<str:tracking_id>/route/', route_view),
        path('admin/cargo/<str:tracking_id>/itineraries/', select_itinerary_view),
        path('admin/cargo/<str:tracking_id>/', cargo_details_view),
    ]
    clear_url_caches()
    with override_settings(ROOT_URLCONF=__name__):
        yield routing_service
    urlpatterns = []
    clear_url_caches()


@pytest.mark.django_db
def test_route_page_renders_cargo_and_numbered_candidate_legs(client, booking_pages):
    response = client.get('/admin/cargo/DEF789/route/')
    content = response.content.decode()
    cargo = DjangoCargoRepository().find(TrackingId('DEF789'))
    assert cargo is not None
    deadline = cargo.route_specification.arrival_deadline

    assert response.status_code == 200
    assert 'Route Cargo DEF789' in content
    assert 'Hong Kong' in content
    assert 'CNHKG' in content
    assert 'Melbourne' in content
    assert 'AUMEL' in content
    assert 'Potential routes: 2' in content
    assert 'Itinerary 1' in content
    assert 'Leg 1' in content
    assert '0200T' in content
    assert 'Hong Kong' in content
    assert 'Rotterdam' in content
    assert 'NLRTM' in content
    assert (deadline - timedelta(days=5)).strftime('%m/%d/%Y') in content
    assert 'Leg 2' in content
    assert '0300A' in content
    assert (deadline - timedelta(days=2)).strftime('%m/%d/%Y') in content
    assert 'Itinerary 2' in content
    assert '0400S' in content
    assert content.count('name="candidate_token"') == 2
    itinerary_one = content.split('Itinerary 1', 1)[1].split('Itinerary 2', 1)[0]
    assert (
        itinerary_one.index('CNHKG') < itinerary_one.index('NLRTM') < itinerary_one.index('AUMEL')
    )
    expected_dates = [
        (deadline - timedelta(days=offset)).strftime('%m/%d/%Y') for offset in (5, 4, 3, 2)
    ]
    assert [itinerary_one.index(date) for date in expected_dates] == sorted(
        itinerary_one.index(date) for date in expected_dates
    )


@pytest.mark.django_db
def test_select_itinerary_renders_candidates_when_routes_exist(client, booking_pages):
    response = client.get('/admin/cargo/DEF789/itineraries/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Potential routes: 2' in content
    assert 'Select Itinerary DEF789' in content
    assert 'Itinerary 1' in content
    assert '0200T' in content
    assert 'Itinerary 2' in content
    assert '0400S' in content


@pytest.mark.django_db
def test_route_page_shows_no_route_guidance_when_candidates_are_empty(client, booking_pages):
    booking_pages.candidates = ()

    response = client.get('/admin/cargo/DEF789/route/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Potential routes: 0' in content
    assert (
        'No routes found that satisfy the route specification. '
        'Try setting an arrival deadline further into the future (a few weeks at least).'
    ) in content
    assert 'name="candidate_index"' not in content


@pytest.mark.django_db
def test_candidate_assignment_redirects_to_cargo_details_and_renders_assigned_itinerary(
    client, booking_pages
):
    selection_page = client.get('/admin/cargo/DEF789/route/')
    candidate_tokens = re.findall(
        r'name="candidate_token"\s+value="([^"]+)"',
        selection_page.content.decode(),
    )
    assert len(candidate_tokens) == 2

    response = client.post(
        '/admin/cargo/DEF789/route/',
        {'candidate_token': candidate_tokens[1]},
    )

    assert response.status_code == 302
    assert response['Location'] == '/admin/cargo/DEF789/'
    assert booking_pages.request_count == 1

    details = client.get(response['Location'])
    content = details.content.decode()

    assert details.status_code == 200
    assert 'Routing Details for Cargo DEF789' in content
    assert 'Hong Kong' in content
    assert 'Melbourne' in content
    assert '0400S' in content
    assert '0200T' not in content


@pytest.mark.django_db
def test_invalid_candidate_token_displays_error_without_requesting_new_candidates(
    client, booking_pages
):
    response = client.post(
        '/admin/cargo/DEF789/route/',
        {'candidate_token': 'invalid'},
    )
    content = response.content.decode()

    assert response.status_code == 400
    assert 'role="alert"' in content
    assert 'Reload the route page and choose an itinerary.' in content
    assert 'href="/admin/cargo/DEF789/route/"' in content
    assert booking_pages.request_count == 0


@pytest.mark.django_db
def test_unknown_cargo_route_selection_returns_not_found(client, booking_pages):
    response = client.get('/admin/cargo/UNKNOWN/route/')

    assert response.status_code == 404
