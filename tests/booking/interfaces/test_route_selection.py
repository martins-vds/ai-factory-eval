from datetime import UTC, datetime

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.booking.interfaces.route_selection.views import (
    create_route_selection_views,
)
from cargotracker.cargo.domain.itinerary import Itinerary
from cargotracker.cargo.domain.leg import Leg
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.location.domain.location import Location
from cargotracker.location.domain.un_locode import UnLocode
from cargotracker.voyage.domain.voyage_number import VoyageNumber
from cargotracker.voyage.infrastructure.repository import DjangoVoyageRepository


class RouteSelectionRouting:
    def __init__(self, candidates=()):
        self.candidates = tuple(candidates)
        self.assigned = None

    def route_candidates(self, tracking_id):
        return self.candidates

    def assign_route(self, tracking_id, itinerary):
        self.assigned = (tracking_id, itinerary)


repository = DjangoCargoRepository()
dashboard = CargoDashboard(repository)
routing = RouteSelectionRouting()
route_view, itineraries_view = create_route_selection_views(routing, dashboard)
_, cargo_details_view = create_booking_views(dashboard)
urlpatterns = [
    path('admin/cargo/<str:tracking_id>/route/', route_view),
    path('admin/cargo/<str:tracking_id>/itineraries/', itineraries_view),
    path('admin/cargo/<str:tracking_id>/', cargo_details_view),
]


@pytest.fixture(autouse=True)
def seed_data():
    call_command('seed_sample_data')
    routing.candidates = ()
    routing.assigned = None


def candidate_itinerary():
    origin = Location(UnLocode('USNYC'), 'New York')
    destination = Location(UnLocode('FIHEL'), 'Helsinki')
    voyage = DjangoVoyageRepository().find(VoyageNumber('0100S'))
    assert voyage is not None
    return Itinerary(
        (
            Leg(
                voyage,
                origin,
                destination,
                datetime(2030, 1, 2, tzinfo=UTC),
                datetime(2030, 1, 4, tzinfo=UTC),
            ),
        )
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_selection_renders_populated_candidates(client):
    itinerary = candidate_itinerary()
    routing.candidates = (itinerary,)

    response = client.get('/admin/cargo/DEF789/route/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Set Route for Cargo DEF789' in content
    assert 'Potential routes:' in content
    assert '1' in content
    assert 'Route option #1' in content
    assert '0100S' in content
    assert 'New York' in content
    assert 'Helsinki' in content
    assert '01/02/2030' in content
    assert '01/04/2030' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_itineraries_renders_populated_candidates(client):
    routing.candidates = (candidate_itinerary(),)

    response = client.get('/admin/cargo/DEF789/itineraries/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Route option #1' in content
    assert '0100S' in content
    assert 'New York' in content
    assert 'Helsinki' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_itineraries_renders_empty_candidate_guidance(client):
    response = client.get('/admin/cargo/DEF789/itineraries/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'No routes found that satisfy the route specification' in content
    assert 'Try setting an arrival deadline further into the future' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_candidate_assignment_redirects_to_cargo_details(client):
    routing.candidates = (candidate_itinerary(),)

    response = client.post(
        '/admin/cargo/DEF789/route/',
        {'candidate': '0'},
    )

    assert response.status_code == 302
    assert response['Location'] == '/admin/cargo/DEF789/'
    assert routing.assigned[0] == TrackingId('DEF789')
    assert routing.assigned[1] == routing.candidates[0]


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_assignment_result_is_visible_on_cargo_details_page(client):
    routing.candidates = (candidate_itinerary(),)
    redirected = client.post('/admin/cargo/DEF789/route/', {'candidate': '0'})
    response = client.get(redirected['Location'])

    assert response.status_code == 200
    assert 'Routing Details for Cargo DEF789' in response.content.decode()
