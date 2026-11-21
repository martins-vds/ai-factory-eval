import re
from datetime import UTC, datetime, timedelta

import pytest
from django.core.management import call_command
from django.http import Http404
from django.test import RequestFactory, override_settings
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.routing import CargoRouting
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.booking.interfaces.route_selection.views import create_route_selection_views
from cargotracker.cargo.domain.itinerary import Itinerary
from cargotracker.cargo.domain.leg import Leg
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository
from cargotracker.voyage.domain.voyage_number import VoyageNumber
from cargotracker.voyage.infrastructure.repository import DjangoVoyageRepository

repository = DjangoCargoRepository()
dashboard = CargoDashboard(repository)


class RoutingStub:
    def __init__(self):
        self.candidates = ()
        self.assigned = None

    def route_candidates(self, tracking_id):
        return self.candidates

    def assign_route(self, tracking_id, itinerary):
        self.assigned = itinerary
        return CargoRouting(
            repository,
            DjangoLocationRepository(),
            DjangoVoyageRepository(),
            DjangoHandlingEventRepository(),
            routing_service=None,
        ).assign_route(tracking_id, itinerary)


routing = RoutingStub()
route_selection_view, itinerary_selection_view, assign_route_view = create_route_selection_views(
    routing, dashboard
)
_, cargo_details_view = create_booking_views(dashboard)
urlpatterns = [
    path('admin/cargo/<str:tracking_id>/route/', route_selection_view),
    path(
        'admin/cargo/<str:tracking_id>/itineraries/',
        itinerary_selection_view,
    ),
    path(
        'admin/cargo/<str:tracking_id>/route/<int:candidate_index>/',
        assign_route_view,
    ),
    path('admin/cargo/<str:tracking_id>/', cargo_details_view),
]


@pytest.fixture(autouse=True)
def reset_routing():
    routing.candidates = ()
    routing.assigned = None


def make_candidate(cargo):
    voyage = DjangoVoyageRepository().find(VoyageNumber('0200T'))
    assert voyage is not None
    return Itinerary(
        (
            Leg(
                voyage,
                cargo.route_specification.origin,
                cargo.route_specification.destination,
                datetime.now(UTC),
                datetime.now(UTC) + timedelta(days=1),
            ),
        )
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_selection_renders_candidate_count_and_numbered_leg(client):
    call_command('seed_sample_data')
    cargo = repository.find(TrackingId('DEF789'))
    assert cargo is not None
    candidate = make_candidate(cargo)
    routing.candidates = (candidate,)

    response = client.get('/admin/cargo/DEF789/route/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Set Route for Cargo DEF789' in content
    assert 'Origin:' in content
    assert cargo.route_specification.origin.name in content
    assert 'Destination:' in content
    assert cargo.route_specification.destination.name in content
    assert 'Potential routes:' in content
    assert re.search(r'Potential routes:</dt>\s*<dd>1</dd>', content)
    assert 'Route option #1' in content
    assert '0200T' in content
    assert cargo.route_specification.origin.name in content
    assert cargo.route_specification.destination.name in content
    assert 'Select' in content
    assert 'No routes found' not in content

    itinerary_response = client.get('/admin/cargo/DEF789/itineraries/')
    itinerary_content = itinerary_response.content.decode()
    assert itinerary_response.status_code == 200
    assert 'Route option #1' in itinerary_content
    assert '0200T' in itinerary_content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_selection_and_itinerary_selection_render_empty_guidance(client):
    call_command('seed_sample_data')

    route_response = client.get('/admin/cargo/DEF789/route/')
    itinerary_response = client.get('/admin/cargo/DEF789/itineraries/')

    assert (
        'No routes found that satisfy the route specification.' in route_response.content.decode()
    )
    itinerary_content = ' '.join(itinerary_response.content.decode().split())
    assert 'Try setting an arrival deadline further into the future' in itinerary_content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_candidate_assignment_redirects_to_cargo_details(client):
    call_command('seed_sample_data')
    cargo = repository.find(TrackingId('DEF789'))
    assert cargo is not None
    candidate = make_candidate(cargo)
    routing.candidates = (candidate,)

    response = client.post('/admin/cargo/DEF789/route/0/')

    assert response.status_code == 302
    assert response.url == '/admin/cargo/DEF789/'
    assert routing.assigned == candidate
    details = client.get(response.url)
    assert details.status_code == 200
    assert 'Routing Details for Cargo DEF789' in details.content.decode()
    assert '0200T' in details.content.decode()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_unknown_cargo_route_and_itinerary_return_http_404(client):
    route_response = client.get('/admin/cargo/UNKNOWN/route/')
    itinerary_response = client.get('/admin/cargo/UNKNOWN/itineraries/')

    assert route_response.status_code == 404
    assert itinerary_response.status_code == 404


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_selection_post_accepts_each_supported_candidate_field(client):
    call_command('seed_sample_data')
    cargo = repository.find(TrackingId('DEF789'))
    assert cargo is not None
    routing.candidates = (make_candidate(cargo),)

    candidate_response = client.post(
        '/admin/cargo/DEF789/route/',
        {'candidate_index': '0'},
    )
    route_response = client.post(
        '/admin/cargo/DEF789/route/',
        {'routeIndex': '0'},
    )
    itinerary_response = client.post(
        '/admin/cargo/DEF789/route/',
        {'itineraryIndex': '0'},
    )

    assert candidate_response.url == '/admin/cargo/DEF789/'
    assert route_response.url == '/admin/cargo/DEF789/'
    assert itinerary_response.url == '/admin/cargo/DEF789/'


def test_assign_candidate_rejects_missing_non_numeric_negative_and_out_of_range_indices():
    with pytest.raises(Http404, match=r'^A route candidate index is required\.$'):
        assign_route_view(RequestFactory().post('/admin/cargo/DEF789/route/'), 'DEF789')
    with pytest.raises(Http404, match=r'^A valid route candidate index is required\.$'):
        assign_route_view(
            RequestFactory().post('/admin/cargo/DEF789/route/', {'candidate_index': 'nope'}),
            'DEF789',
        )
    for index in (-1, 1):
        with pytest.raises(Http404, match=r'^The route candidate was not found\.$'):
            assign_route_view(
                RequestFactory().post('/admin/cargo/DEF789/route/'),
                'DEF789',
                index,
            )
