import sys
from datetime import UTC, datetime

import pytest
from django.core.management import call_command
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.registration import CargoRegistration
from cargotracker.booking.application.routing import CargoRouting
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.booking.interfaces.route_selection.views import create_route_selection_views
from cargotracker.cargo.domain.itinerary import Itinerary
from cargotracker.cargo.domain.leg import Leg
from cargotracker.cargo.domain.repository import CargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.domain.location import Location
from cargotracker.location.domain.un_locode import UnLocode
from cargotracker.location.infrastructure.models import LocationRecord
from cargotracker.location.infrastructure.repository import DjangoLocationRepository
from cargotracker.pathfinder.domain.transit_edge import TransitEdge
from cargotracker.pathfinder.domain.transit_path import TransitPath
from cargotracker.voyage.domain.voyage_number import VoyageNumber
from cargotracker.voyage.infrastructure.models import VoyageRecord
from cargotracker.voyage.infrastructure.repository import DjangoVoyageRepository

ORIGIN = Location(UnLocode('USNYC'), 'New York')
TRANSFER = Location(UnLocode('NLRTM'), 'Rotterdam')
DESTINATION = Location(UnLocode('FIHEL'), 'Helsinki')
DEADLINE = datetime(2030, 11, 5, tzinfo=UTC)


class CandidateRoutingService:
    def __init__(self, candidates):
        self.candidates = candidates

    def find_shortest_paths(self, origin, destination):
        return self.candidates


def _edge(voyage, from_port, to_port, departure, arrival):
    return TransitEdge(
        voyage,
        from_port,
        to_port,
        datetime(2030, 11, departure, tzinfo=UTC),
        datetime(2030, 11, arrival, tzinfo=UTC),
    )


def _candidate_paths():
    return (
        TransitPath(
            (
                _edge('CM001', 'USNYC', 'NLRTM', 1, 2),
                _edge('CM002', 'NLRTM', 'FIHEL', 3, 4),
            )
        ),
        TransitPath((_edge('CM003', 'USNYC', 'FIHEL', 2, 4),)),
    )


@pytest.fixture
def route_pages(settings, monkeypatch):
    settings.ROOT_URLCONF = __name__

    def configure(candidates):
        for location in (ORIGIN, TRANSFER, DESTINATION):
            LocationRecord.objects.get_or_create(
                unlocode=location.unlocode.value,
                defaults={'name': location.name},
            )
        for voyage_number in ('CM001', 'CM002', 'CM003'):
            VoyageRecord.objects.get_or_create(voyage_number=voyage_number)

        cargo_repository: CargoRepository = DjangoCargoRepository()
        tracking_id = CargoRegistration(cargo_repository).register(ORIGIN, DESTINATION, DEADLINE)
        dashboard = CargoDashboard(cargo_repository)
        routing = CargoRouting(
            cargo_repository,
            DjangoLocationRepository(),
            DjangoVoyageRepository(),
            DjangoHandlingEventRepository(),
            CandidateRoutingService(candidates),
        )
        route_view, itinerary_view = create_route_selection_views(routing, dashboard)
        _, cargo_details_view = create_booking_views(dashboard)
        monkeypatch.setattr(
            sys.modules[__name__],
            'urlpatterns',
            [
                path('admin/cargo/<str:tracking_id>/route/', route_view),
                path('admin/cargo/<str:tracking_id>/itineraries/', itinerary_view),
                path('admin/cargo/<str:tracking_id>/', cargo_details_view),
            ],
            raising=False,
        )
        return tracking_id

    return configure


@pytest.mark.django_db
def test_route_page_renders_cargo_details_and_candidate_properties(client, route_pages):
    tracking_id = route_pages(_candidate_paths())

    response = client.get(f'/admin/cargo/{tracking_id.value}/route/')
    content = response.content.decode()

    assert response.status_code == 200
    assert f'Routing Details for Cargo {tracking_id.value}' in content
    assert 'New York' in content and 'USNYC' in content
    assert 'Helsinki' in content and 'FIHEL' in content
    assert '11/05/2030' in content
    assert 'Potential routes: 2' in content
    assert 'Route 1' in content and 'Route 2' in content
    assert 'Leg 1' in content and 'Leg 2' in content
    assert 'CM001' in content and 'Rotterdam' in content

    itineraries = [candidate['itinerary'] for candidate in response.context['route_candidates']]
    assert itineraries
    for itinerary in itineraries:
        assert itinerary is not None
        assert itinerary.legs
        assert itinerary.legs[0].load_location == ORIGIN
        assert itinerary.legs[-1].unload_location == DESTINATION
        assert all(
            first.unload_location == following.load_location
            for first, following in zip(itinerary.legs, itinerary.legs[1:])
        )


@pytest.mark.django_db
def test_select_itinerary_renders_candidates_when_present(client, route_pages):
    tracking_id = route_pages(_candidate_paths())

    response = client.get(f'/admin/cargo/{tracking_id.value}/itineraries/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Potential routes: 2' in content
    assert 'Route 1' in content and 'Route 2' in content
    assert 'Select itinerary' in content
    assert 'No routes found' not in content


@pytest.mark.django_db
def test_route_pages_show_no_route_guidance_when_candidates_are_empty(client, route_pages):
    tracking_id = route_pages(())

    route_response = client.get(f'/admin/cargo/{tracking_id.value}/route/')
    itinerary_response = client.get(f'/admin/cargo/{tracking_id.value}/itineraries/')

    guidance = (
        'No routes found that satisfy the route specification. '
        'Try setting an arrival deadline further into the future (a few weeks at least).'
    )
    assert route_response.status_code == 200
    assert itinerary_response.status_code == 200
    assert guidance in route_response.content.decode()
    assert guidance in itinerary_response.content.decode()


@pytest.mark.django_db
def test_assigning_candidate_redirects_to_cargo_details_and_shows_selected_itinerary(
    client, route_pages
):
    tracking_id = route_pages(_candidate_paths())
    itinerary_response = client.get(f'/admin/cargo/{tracking_id.value}/itineraries/')
    selected_candidate = itinerary_response.context['route_candidates'][1]

    assignment_response = client.post(
        f'/admin/cargo/{tracking_id.value}/itineraries/',
        {'itinerary_token': selected_candidate['token']},
    )

    assert assignment_response.status_code == 302
    assert assignment_response.url == f'/admin/cargo/{tracking_id.value}/'

    details_response = client.get(assignment_response.url)
    content = details_response.content.decode()
    assert details_response.status_code == 200
    assert 'Routing Details' in content
    assert 'CM003' in content
    assert 'CM001' not in content
    assert 'Itinerary' in content
