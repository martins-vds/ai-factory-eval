import html
import re
from datetime import UTC, datetime
from itertools import pairwise

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.routing import CargoRouting
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.booking.interfaces.route_selection.views import create_route_selection_views
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.models import CargoRecord
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository
from cargotracker.pathfinder.domain.transit_edge import TransitEdge
from cargotracker.pathfinder.domain.transit_path import TransitPath
from cargotracker.voyage.infrastructure.repository import DjangoVoyageRepository

ORIGIN = 'CNHKG'
TRANSFER = 'NLRTM'
DESTINATION = 'AUMEL'
DEPARTURE = datetime(2026, 11, 8, tzinfo=UTC)


class CandidateRoutingService:
    def __init__(self):
        self.candidates = ()

    def find_shortest_paths(self, origin, destination):
        assert (origin, destination) == (ORIGIN, DESTINATION)
        return self.candidates


routing_service = CandidateRoutingService()
cargo_repository = DjangoCargoRepository()
cargo_dashboard = CargoDashboard(cargo_repository)
cargo_routing = CargoRouting(
    cargo_repository,
    DjangoLocationRepository(),
    DjangoVoyageRepository(),
    DjangoHandlingEventRepository(),
    routing_service,
)
route_view, select_itinerary_view = create_route_selection_views(cargo_dashboard, cargo_routing)
_, cargo_details_view = create_booking_views(cargo_dashboard)
urlpatterns = [
    path('admin/cargo/<str:tracking_id>/route/', route_view),
    path('admin/cargo/<str:tracking_id>/itineraries/', select_itinerary_view),
    path('admin/cargo/<str:tracking_id>/', cargo_details_view),
]


def _candidate_paths():
    return (
        TransitPath(
            (
                TransitEdge(
                    '0100S',
                    ORIGIN,
                    TRANSFER,
                    DEPARTURE,
                    datetime(2026, 11, 10, tzinfo=UTC),
                ),
                TransitEdge(
                    '0200T',
                    TRANSFER,
                    DESTINATION,
                    datetime(2026, 11, 11, tzinfo=UTC),
                    datetime(2026, 11, 13, tzinfo=UTC),
                ),
            )
        ),
        TransitPath(
            (
                TransitEdge(
                    '0300A',
                    ORIGIN,
                    DESTINATION,
                    datetime(2026, 11, 15, tzinfo=UTC),
                    datetime(2026, 11, 20, tzinfo=UTC),
                ),
            )
        ),
    )


@pytest.fixture(autouse=True)
def reset_routing_service(monkeypatch):
    routing_service.candidates = ()
    monkeypatch.setattr(
        'cargotracker.cargo.management.commands.seed_sample_data.timezone.now',
        lambda: datetime(2026, 11, 7, tzinfo=UTC),
    )


@pytest.fixture
def seeded_cargo():
    call_command('seed_sample_data')
    return TrackingId('DEF789')


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_page_displays_cargo_candidate_count_and_numbered_connected_legs(
    seeded_cargo, client
):
    routing_service.candidates = _candidate_paths()

    response = client.get(f'/admin/cargo/{seeded_cargo.value}/route/')
    content = response.content.decode()
    candidates = response.context['candidates']

    assert response.status_code == 200
    assert len(candidates) == 2
    assert 'Route Cargo DEF789' in content
    assert 'Hong Kong (CNHKG)' in content
    assert 'Melbourne' in content
    assert 'AUMEL' in content
    assert 'Potential routes: 2' in content
    assert 'Route 1' in content
    assert 'Leg 1' in content
    assert 'Leg 2' in content
    assert candidates is not None
    for candidate in candidates:
        legs = candidate['itinerary'].legs
        assert legs
        assert legs[0].load_location.unlocode.value == ORIGIN
        assert legs[-1].unload_location.unlocode.value == DESTINATION
        assert all(
            previous.unload_location == following.load_location
            for previous, following in pairwise(legs)
        )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_select_itinerary_displays_candidates_when_routes_exist(seeded_cargo, client):
    routing_service.candidates = _candidate_paths()

    response = client.get(f'/admin/cargo/{seeded_cargo.value}/itineraries/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Select Itinerary DEF789' in content
    assert 'Potential routes: 2' in content
    assert 'Route 1' in content
    assert 'Route 2' in content
    assert 'No routes found that satisfy the route specification.' not in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
@pytest.mark.parametrize('screen', ('route', 'itineraries'))
def test_route_screens_show_no_route_guidance_when_candidates_are_empty(
    seeded_cargo, client, screen
):
    response = client.get(f'/admin/cargo/{seeded_cargo.value}/{screen}/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Potential routes: 0' in content
    assert 'No routes found that satisfy the route specification.' in content
    assert 'Try setting an arrival deadline further into the future.' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
@pytest.mark.parametrize('screen', ('route', 'itineraries'))
def test_unknown_cargo_route_screens_return_http_404(client, screen):
    response = client.get(f'/admin/cargo/UNKNOWN/{screen}/')

    assert response.status_code == 404


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_assignment_rejects_a_modified_candidate_token(seeded_cargo, client):
    response = client.post(
        f'/admin/cargo/{seeded_cargo.value}/itineraries/',
        {'candidate': 'not-a-server-signed-candidate'},
    )
    details_response = client.get(f'/admin/cargo/{seeded_cargo.value}/')

    assert response.status_code == 400
    assert response.content == b'Invalid route selection.'
    assert details_response.status_code == 200
    assert '<strong>Not routed</strong>' in details_response.content.decode()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_selecting_a_candidate_redirects_to_details_with_the_assigned_itinerary(
    seeded_cargo, client
):
    routing_service.candidates = _candidate_paths()
    route_response = client.get(f'/admin/cargo/{seeded_cargo.value}/route/')
    token_match = re.search(
        r'name="candidate"\s+value="([^"]+)"',
        route_response.content.decode(),
    )
    assert token_match is not None
    candidate_token = html.unescape(token_match.group(1))

    response = client.post(
        f'/admin/cargo/{seeded_cargo.value}/itineraries/',
        {'candidate': candidate_token},
    )

    assert response.status_code == 302
    assert response.headers['Location'] == f'/admin/cargo/{seeded_cargo.value}/'
    details_response = client.get(response.headers['Location'])
    details = details_response.content.decode()

    assert details_response.status_code == 200
    assert 'Routing Details for Cargo DEF789' in details
    assert '0100S' in details
    assert '0200T' in details
    assert 'Rotterdam' in details
    assert 'Melbourne' in details


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_assignment_encodes_tracking_id_in_details_redirect(seeded_cargo, client):
    tracking_id = 'DEF#789'
    CargoRecord.objects.filter(tracking_id=seeded_cargo.value).update(tracking_id=tracking_id)
    routing_service.candidates = _candidate_paths()
    route_response = client.get('/admin/cargo/DEF%23789/route/')
    token_match = re.search(
        r'name="candidate"\s+value="([^"]+)"',
        route_response.content.decode(),
    )
    assert token_match is not None
    candidate_token = html.unescape(token_match.group(1))

    response = client.post(
        '/admin/cargo/DEF%23789/itineraries/',
        {'candidate': candidate_token},
    )

    assert response.status_code == 302
    assert response.headers['Location'] == '/admin/cargo/DEF%23789/'
