import re
from datetime import UTC, datetime

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.routing import CargoRouting
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.booking.interfaces.route_selection.views import (
    create_route_selection_view,
)
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.cargo.management.commands import seed_sample_data
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository
from cargotracker.pathfinder.domain.transit_edge import TransitEdge
from cargotracker.pathfinder.domain.transit_path import TransitPath
from cargotracker.voyage.infrastructure.repository import DjangoVoyageRepository


class CandidateRoutingService:
    def __init__(self):
        self.candidates = ()

    def find_shortest_paths(self, origin, destination):
        return self.candidates


routing_service = CandidateRoutingService()
cargo_repository = DjangoCargoRepository()
location_repository = DjangoLocationRepository()
voyage_repository = DjangoVoyageRepository()
cargo_dashboard = CargoDashboard(cargo_repository)
cargo_routing = CargoRouting(
    cargo_repository,
    location_repository,
    voyage_repository,
    DjangoHandlingEventRepository(),
    routing_service,
)
route_selection_view = create_route_selection_view(
    cargo_routing,
    cargo_dashboard,
)
_, cargo_details_view = create_booking_views(cargo_dashboard)
urlpatterns = [
    path('admin/cargo/<str:tracking_id>/route/', route_selection_view),
    path('admin/cargo/<str:tracking_id>/', cargo_details_view),
]


@pytest.fixture(autouse=True)
def reset_routing_candidates():
    routing_service.candidates = ()


def _seed_sample_data(monkeypatch):
    monkeypatch.setattr(
        seed_sample_data.timezone,
        'now',
        lambda: datetime(2026, 11, 7, tzinfo=UTC),
    )
    call_command('seed_sample_data')


def _candidate_paths():
    return (
        TransitPath(
            (
                TransitEdge(
                    '0300A',
                    'CNHKG',
                    'JNTKO',
                    datetime(2026, 11, 10, tzinfo=UTC),
                    datetime(2026, 11, 11, tzinfo=UTC),
                ),
                TransitEdge(
                    '0200T',
                    'JNTKO',
                    'AUMEL',
                    datetime(2026, 11, 12, tzinfo=UTC),
                    datetime(2026, 11, 14, tzinfo=UTC),
                ),
            )
        ),
        TransitPath(
            (
                TransitEdge(
                    '0400S',
                    'CNHKG',
                    'AUMEL',
                    datetime(2026, 11, 15, tzinfo=UTC),
                    datetime(2026, 11, 17, tzinfo=UTC),
                ),
            )
        ),
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_selection_renders_candidate_itinerary_properties_as_target_behavior(
    client, monkeypatch
):
    _seed_sample_data(monkeypatch)
    routing_service.candidates = _candidate_paths()

    response = client.get('/admin/cargo/DEF789/route/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Route Cargo DEF789' in content
    assert 'Hong Kong (CNHKG)' in content
    assert 'Melbourne (AUMEL)' in content
    assert '01/07/2027' in content
    assert 'Potential routes: 2' in content
    assert 'Candidate 1' in content and 'Candidate 2' in content
    assert 'Leg 1' in content and 'Leg 2' in content
    assert '0300A' in content and '0200T' in content and '0400S' in content
    assert 'Tokyo (JNTKO)' in content
    assert '11/10/2026' in content and '11/14/2026' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_selection_shows_no_route_guidance_when_candidates_are_empty(client, monkeypatch):
    _seed_sample_data(monkeypatch)

    response = client.get('/admin/cargo/DEF789/route/')
    content = response.content.decode()
    normalized_content = ' '.join(content.split())

    assert response.status_code == 200
    assert 'Potential routes: 0' in content
    assert (
        'No routes found that satisfy the route specification. '
        'Try setting an arrival deadline further into the future (a few weeks at least).'
    ) in normalized_content
    assert 'Candidate 1' not in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_selection_assigns_selected_candidate_and_redirects_to_cargo_details(
    client, monkeypatch
):
    _seed_sample_data(monkeypatch)
    routing_service.candidates = _candidate_paths()
    route_url = '/admin/cargo/DEF789/route/'
    response = client.get(route_url)
    token = re.search(r'name="candidate_token"\s+value="([^"]+)"', response.content.decode()).group(
        1
    )

    response = client.post(route_url, {'candidate_token': token}, follow=True)
    content = response.content.decode()

    assert response.status_code == 200
    assert response.redirect_chain == [('/admin/cargo/DEF789/', 302)]
    assert 'Routing Details for Cargo DEF789' in content
    assert 'Itinerary' in content
    assert '0300A' in content and '0200T' in content
    assert '0400S' not in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_selection_rejects_an_invalid_candidate_token(client, monkeypatch):
    _seed_sample_data(monkeypatch)

    response = client.post(
        '/admin/cargo/DEF789/route/',
        {'candidate_token': 'not-a-valid-signature'},
    )

    assert response.status_code == 400
    assert response.content == b'Invalid route selection.'
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    assert not cargo.itinerary.legs


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_selection_rejects_a_candidate_token_for_another_cargo(client, monkeypatch):
    _seed_sample_data(monkeypatch)
    routing_service.candidates = _candidate_paths()
    cargo = cargo_repository.find(TrackingId('ABC123'))
    assert cargo is not None
    response = client.get('/admin/cargo/DEF789/route/')
    token = re.search(r'name="candidate_token"\s+value="([^"]+)"', response.content.decode()).group(
        1
    )

    response = client.post(
        '/admin/cargo/ABC123/route/',
        {'candidate_token': token},
    )
    updated_cargo = cargo_repository.find(TrackingId('ABC123'))

    assert response.status_code == 400
    assert updated_cargo is not None
    assert updated_cargo.itinerary == cargo.itinerary
