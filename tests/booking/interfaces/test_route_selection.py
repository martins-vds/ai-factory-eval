from datetime import UTC, datetime

import pytest
from django.http import Http404
from django.test import RequestFactory, override_settings
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.registration import CargoRegistration
from cargotracker.booking.application.routing import CargoRouting
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.domain.location import Location
from cargotracker.location.domain.un_locode import UnLocode
from cargotracker.location.infrastructure.models import LocationRecord
from cargotracker.location.infrastructure.repository import DjangoLocationRepository
from cargotracker.pathfinder.domain.transit_edge import TransitEdge
from cargotracker.pathfinder.domain.transit_path import TransitPath
from cargotracker.voyage.infrastructure.models import VoyageRecord
from cargotracker.voyage.infrastructure.repository import DjangoVoyageRepository

ORIGIN = Location(UnLocode('USNYC'), 'New York')
TRANSFER = Location(UnLocode('NLRTM'), 'Rotterdam')
DESTINATION = Location(UnLocode('FIHEL'), 'Helsinki')
DEADLINE = datetime(2030, 11, 5, tzinfo=UTC)


class CandidateRoutingService:
    def __init__(self):
        self.paths = ()

    def find_shortest_paths(self, origin, destination):
        return self.paths


def _edge(voyage, from_port, to_port, departure, arrival):
    return TransitEdge(
        voyage,
        from_port,
        to_port,
        datetime(2030, 11, departure, tzinfo=UTC),
        datetime(2030, 11, arrival, tzinfo=UTC),
    )


repository = DjangoCargoRepository()
candidate_routing_service = CandidateRoutingService()
cargo_routing = CargoRouting(
    repository,
    DjangoLocationRepository(),
    DjangoVoyageRepository(),
    DjangoHandlingEventRepository(),
    candidate_routing_service,
)
dashboard_view, cargo_details_view = create_booking_views(CargoDashboard(repository))


def _route_selection_views():
    from cargotracker.booking.interfaces.route_selection.views import (
        create_route_selection_views,
    )

    return create_route_selection_views(cargo_routing, CargoDashboard(repository))


route_selection_view, select_itinerary_view = _route_selection_views()
urlpatterns = [
    path('admin/cargo/<str:tracking_id>/route/', route_selection_view),
    path('admin/cargo/<str:tracking_id>/itineraries/', select_itinerary_view),
    path('admin/cargo/<str:tracking_id>/', cargo_details_view),
]


@pytest.fixture(autouse=True)
def clear_candidate_paths():
    candidate_routing_service.paths = ()


def _register_cargo():
    for location in (ORIGIN, TRANSFER, DESTINATION):
        LocationRecord.objects.create(
            unlocode=location.unlocode.value,
            name=location.name,
        )
    for voyage_number in ('CM001', 'CM002', 'CM003'):
        VoyageRecord.objects.create(voyage_number=voyage_number)
    tracking_id = CargoRegistration(repository).register(ORIGIN, DESTINATION, DEADLINE)
    return tracking_id.value


def _candidate_paths():
    return (
        TransitPath(
            (
                _edge('CM001', 'USNYC', 'NLRTM', 1, 2),
                _edge('CM002', 'NLRTM', 'FIHEL', 3, 4),
            )
        ),
        TransitPath((_edge('CM003', 'USNYC', 'FIHEL', 2, 3),)),
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_selection_renders_details_count_and_numbered_candidates(client):
    tracking_id = _register_cargo()
    candidate_routing_service.paths = _candidate_paths()

    response = client.get(f'/admin/cargo/{tracking_id}/route/')
    content = ' '.join(response.content.decode().split())
    candidates = response.context['candidates']

    assert response.status_code == 200
    assert f'Route Cargo {tracking_id}' in content
    assert 'New York (USNYC)' in content
    assert 'Helsinki (FIHEL)' in content
    assert 'Arrival deadline:' in content
    assert 'Potential routes: 2' in content
    assert 'Candidate route 1' in content
    assert 'Candidate route 2' in content
    assert 'Leg 1' in content
    assert 'Leg 2' in content
    assert len(candidates) == 2
    assert all(candidate.legs for candidate in candidates)
    assert candidates[0].legs[0].load_location == ORIGIN
    assert candidates[0].legs[-1].unload_location == DESTINATION
    assert all(
        first.unload_location == second.load_location
        for candidate in candidates
        for first, second in zip(candidate.legs, candidate.legs[1:])
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_select_itinerary_renders_populated_candidates(client):
    tracking_id = _register_cargo()
    candidate_routing_service.paths = _candidate_paths()

    response = client.get(f'/admin/cargo/{tracking_id}/itineraries/')
    content = ' '.join(response.content.decode().split())

    assert response.status_code == 200
    assert 'Potential routes: 2' in content
    assert 'Candidate route 1' in content
    assert 'Candidate route 2' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_select_itinerary_shows_no_route_guidance_when_candidates_are_empty(client):
    tracking_id = _register_cargo()

    response = client.get(f'/admin/cargo/{tracking_id}/itineraries/')
    content = ' '.join(response.content.decode().split())

    assert response.status_code == 200
    assert 'Potential routes: 0' in content
    assert (
        'No routes found that satisfy the route specification. Try setting an '
        'arrival deadline further into the future (a few weeks at least).'
    ) in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_assign_candidate_redirects_to_cargo_details_and_shows_assigned_itinerary(client):
    tracking_id = _register_cargo()
    candidate_routing_service.paths = _candidate_paths()

    selection_response = client.get(f'/admin/cargo/{tracking_id}/route/')
    candidate_token = selection_response.context['candidate_options'][0]['token']
    response = client.post(
        f'/admin/cargo/{tracking_id}/route/',
        {'candidate_token': candidate_token},
    )

    assert response.status_code == 302
    assert response.url == f'/admin/cargo/{tracking_id}/'

    details_response = client.get(response.url)
    content = ' '.join(details_response.content.decode().split())

    assert details_response.status_code == 200
    assert f'Routing Details for Cargo {tracking_id}' in content
    assert 'Itinerary' in content
    assert 'CM001' in content
    assert 'CM002' in content
    assert 'Rotterdam' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_selection_rejects_tampered_candidate_token(client):
    tracking_id = _register_cargo()
    candidate_routing_service.paths = _candidate_paths()

    response = client.post(
        f'/admin/cargo/{tracking_id}/route/',
        {'candidate_token': 'tampered-token'},
    )

    assert response.status_code == 400


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_selection_does_not_assign_a_token_to_another_cargo(client):
    tracking_id = _register_cargo()
    candidate_routing_service.paths = _candidate_paths()
    selection_response = client.get(f'/admin/cargo/{tracking_id}/route/')
    candidate_token = selection_response.context['candidate_options'][0]['token']
    other_tracking_id = CargoRegistration(repository).register(
        ORIGIN, DESTINATION, DEADLINE
    ).value

    response = client.post(
        f'/admin/cargo/{other_tracking_id}/route/',
        {'candidate_token': candidate_token},
    )

    assert response.status_code == 400
    other_cargo = repository.find(TrackingId(other_tracking_id))
    assert other_cargo is not None
    assert other_cargo.itinerary.legs == ()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_selection_raises_not_found_for_unknown_cargo():
    with pytest.raises(Http404, match=r'^Cargo with tracking ID MISSING1 not found\.$'):
        route_selection_view(RequestFactory().get('/admin/cargo/MISSING1/route/'), 'MISSING1')


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_selection_rejects_unsupported_methods(client):
    tracking_id = _register_cargo()

    response = client.put(f'/admin/cargo/{tracking_id}/route/')

    assert response.status_code == 405
    assert response.headers['Allow'] == 'GET, POST'
