from datetime import UTC, datetime

import pytest
from django.core import signing
from django.http import Http404
from django.test import RequestFactory, override_settings
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.registration import CargoRegistration
from cargotracker.booking.application.routing import CargoRouting
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.booking.interfaces.route_selection.views import (
    create_route_selection_views,
)
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
        self.candidates = ()

    def find_shortest_paths(self, origin, destination):
        return self.candidates


class Repository:
    def __init__(self):
        self.cargo = DjangoCargoRepository()

    def find(self, tracking_id):
        return self.cargo.find(tracking_id)

    def find_all(self):
        return self.cargo.find_all()

    def upsert(self, cargo):
        return self.cargo.upsert(cargo)


repository = Repository()
dashboard = CargoDashboard(repository)
routing_service = CandidateRoutingService()
routing = CargoRouting(
    repository,
    DjangoLocationRepository(),
    DjangoVoyageRepository(),
    DjangoHandlingEventRepository(),
    routing_service,
)
route_selection_view, select_itinerary_view = create_route_selection_views(routing, dashboard)
_, cargo_details_view = create_booking_views(dashboard)
urlpatterns = [
    path('admin/cargo/<str:tracking_id>/route/', route_selection_view),
    path('admin/cargo/<str:tracking_id>/itineraries/', select_itinerary_view),
    path('admin/cargo/<str:tracking_id>/', cargo_details_view, name='cargo_details'),
]


@pytest.fixture(autouse=True)
def reset_routing_service():
    routing_service.candidates = ()


def _edge(voyage, from_port, to_port, departure, arrival):
    return TransitEdge(
        voyage,
        from_port,
        to_port,
        datetime(2030, 11, departure, tzinfo=UTC),
        datetime(2030, 11, arrival, tzinfo=UTC),
    )


def _register_cargo_and_candidates():
    for location in (ORIGIN, TRANSFER, DESTINATION):
        LocationRecord.objects.create(
            unlocode=location.unlocode.value,
            name=location.name,
        )
    for voyage_number in ('CM001', 'CM002', 'CM003'):
        VoyageRecord.objects.create(voyage_number=voyage_number)

    tracking_id = CargoRegistration(repository).register(ORIGIN, DESTINATION, DEADLINE)
    routing_service.candidates = (
        TransitPath(
            (
                _edge('CM001', 'USNYC', 'NLRTM', 1, 2),
                _edge('CM002', 'NLRTM', 'FIHEL', 3, 4),
            )
        ),
        TransitPath((_edge('CM003', 'USNYC', 'FIHEL', 2, 4),)),
    )
    return tracking_id


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_selection_renders_candidate_details_and_target_route_properties(client):
    tracking_id = _register_cargo_and_candidates()

    response = client.get(f'/admin/cargo/{tracking_id.value}/route/')
    content = response.content.decode()

    assert response.status_code == 200
    assert f'Routing Details for Cargo {tracking_id.value}' in content
    assert 'New York' in content and 'USNYC' in content
    assert 'Helsinki' in content and 'FIHEL' in content
    assert 'Arrival deadline:' in content
    assert 'Potential routes: 2' in content
    assert 'Itinerary 1' in content and 'Itinerary 2' in content
    assert 'CM001' in content and 'Rotterdam' in content
    assert 'Leg 1' in content and 'Leg 2' in content

    itineraries = [route['itinerary'] for route in response.context['routes']]
    assert len(itineraries) == 2
    for itinerary in itineraries:
        assert itinerary.legs
        assert itinerary.legs[0].load_location == ORIGIN
        assert itinerary.legs[-1].unload_location == DESTINATION
        assert all(
            first.unload_location == second.load_location
            for first, second in zip(itinerary.legs, itinerary.legs[1:])
        )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_selection_shows_no_route_guidance_when_candidates_are_empty(client):
    tracking_id = _register_cargo_and_candidates()
    routing_service.candidates = ()

    response = client.get(f'/admin/cargo/{tracking_id.value}/route/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Potential routes: 0' in content
    assert (
        'No routes found that satisfy the route specification. '
        'Try setting an arrival deadline further into the future.'
    ) in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_select_itinerary_renders_candidates_when_present(client):
    tracking_id = _register_cargo_and_candidates()

    response = client.get(f'/admin/cargo/{tracking_id.value}/itineraries/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Potential routes: 2' in content
    assert 'Itinerary 1' in content and 'Itinerary 2' in content
    assert 'CM001' in content and 'CM003' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_select_itinerary_shows_no_route_guidance_when_candidates_are_empty(client):
    tracking_id = _register_cargo_and_candidates()
    routing_service.candidates = ()

    response = client.get(f'/admin/cargo/{tracking_id.value}/itineraries/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Potential routes: 0' in content
    assert (
        'No routes found that satisfy the route specification. '
        'Try setting an arrival deadline further into the future (a few weeks at least).'
    ) in content
    assert 'Itinerary 1' not in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_assigning_displayed_candidate_redirects_to_details_and_persists_itinerary(client):
    tracking_id = _register_cargo_and_candidates()
    route_page = client.get(f'/admin/cargo/{tracking_id.value}/route/')
    first_candidate = route_page.context['routes'][0]['selection']
    routing_service.candidates = ()

    response = client.post(
        f'/admin/cargo/{tracking_id.value}/route/',
        {'candidate': first_candidate},
        follow=True,
    )
    content = response.content.decode()

    assert response.status_code == 200
    assert response.redirect_chain == [(f'/admin/cargo/{tracking_id.value}/', 302)]
    assert f'Routing Details for Cargo {tracking_id.value}' in content
    assert 'Itinerary' in content
    assert 'CM001' in content
    assert 'Rotterdam' in content
    assert 'CM003' not in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_selection_rejects_an_invalid_candidate_token(client):
    tracking_id = _register_cargo_and_candidates()

    response = client.post(
        f'/admin/cargo/{tracking_id.value}/route/',
        {'candidate': 'not-a-signed-candidate'},
    )

    assert response.status_code == 400
    assert response.content == b'Invalid route selection.'


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_selection_rejects_a_candidate_for_another_cargo(client):
    first_tracking_id = _register_cargo_and_candidates()
    second_tracking_id = CargoRegistration(repository).register(ORIGIN, DESTINATION, DEADLINE)
    candidate = client.get(f'/admin/cargo/{first_tracking_id.value}/route/').context['routes'][0][
        'selection'
    ]

    response = client.post(
        f'/admin/cargo/{second_tracking_id.value}/route/',
        {'candidate': candidate},
    )

    assert response.status_code == 400
    assert response.content == b'Invalid route selection.'


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_selection_rejects_a_signed_non_mapping_candidate(client):
    tracking_id = _register_cargo_and_candidates()
    candidate = signing.dumps(
        'not a mapping',
        salt='cargotracker.booking.route_selection',
    )

    response = client.post(
        f'/admin/cargo/{tracking_id.value}/route/',
        {'candidate': candidate},
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_unknown_route_selection_raises_the_existing_not_found_error():
    with pytest.raises(Http404, match=r'^Cargo with tracking ID UNKNOWN not found\.$'):
        route_selection_view(
            RequestFactory().get('/admin/cargo/UNKNOWN/route/'),
            'UNKNOWN',
        )
