from datetime import UTC, datetime, timedelta

import pytest
from django.core.management import call_command
from django.http import Http404
from django.test import RequestFactory, override_settings
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.routing import CargoRouting
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.booking.interfaces.route_selection.views import (
    create_route_selection_views,
)
from cargotracker.cargo.domain.itinerary import Itinerary
from cargotracker.cargo.domain.leg import Leg
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository
from cargotracker.voyage.domain.voyage_number import VoyageNumber
from cargotracker.voyage.infrastructure.repository import DjangoVoyageRepository


class RouteSelectionRepository(DjangoCargoRepository):
    def __init__(self):
        super().__init__()
        self.candidates = ()
        self.assigned = None


repository = RouteSelectionRepository()
dashboard = CargoDashboard(repository)


class RoutingForTest(CargoRouting):
    def __init__(self):
        self.candidates = ()
        self.assigned = None
        self._real_routing = CargoRouting(
            DjangoCargoRepository(),
            DjangoLocationRepository(),
            DjangoVoyageRepository(),
            DjangoHandlingEventRepository(),
            routing_service=None,
        )

    def route_candidates(self, tracking_id):
        return self.candidates

    def assign_route(self, tracking_id, itinerary):
        self.assigned = (tracking_id, itinerary)
        return self._real_routing.assign_route(tracking_id, itinerary)


routing = RoutingForTest()
route_view, itinerary_view = create_route_selection_views(routing, dashboard)
_, cargo_details_view = create_booking_views(dashboard)
urlpatterns = [
    path('admin/cargo/<str:tracking_id>/route/', route_view),
    path('admin/cargo/<str:tracking_id>/itineraries/', itinerary_view),
    path('admin/cargo/<str:tracking_id>/', cargo_details_view),
]


@pytest.fixture(autouse=True)
def reset_route_selection():
    routing.candidates = ()
    routing.assigned = None
    repository.candidates = ()
    repository.assigned = None


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_selection_renders_candidate_count_and_numbered_legs(client):
    call_command('seed_sample_data')
    cargo = repository.find(TrackingId('DEF789'))
    assert cargo is not None
    origin = cargo.route_specification.origin
    destination = cargo.route_specification.destination
    voyage = DjangoVoyageRepository().find(VoyageNumber('0100S'))
    assert voyage is not None
    routing.candidates = (
        Itinerary(
            (
                Leg(
                    voyage,
                    origin,
                    destination,
                    datetime(2026, 11, 1, tzinfo=UTC),
                    datetime(2026, 11, 2, tzinfo=UTC),
                ),
            )
        ),
    )

    response = client.get('/admin/cargo/DEF789/route/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'DEF789' in content
    assert 'Hong Kong' in content
    assert 'Melbourne' in content
    assert 'Potential routes:' in content
    assert 'Potential routes:</strong> 1' in content
    assert 'Route option #1' in content
    assert '0100S' in content
    assert 'CNHKG' in content
    assert 'AUMEL' in content
    assert '11/01/2026' in content
    assert '11/02/2026' in content
    assert 'Select' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_selection_renders_empty_candidate_guidance(client):
    call_command('seed_sample_data')

    response = client.get('/admin/cargo/DEF789/route/')

    assert response.status_code == 200
    assert 'No routes found that satisfy the route specification.' in response.content.decode()
    assert 'Try setting an arrival deadline further into the future.' in response.content.decode()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_itinerary_selection_renders_candidates_and_empty_state(client):
    call_command('seed_sample_data')
    cargo = repository.find(TrackingId('DEF789'))
    assert cargo is not None
    voyage = DjangoVoyageRepository().find(VoyageNumber('0100S'))
    assert voyage is not None
    routing.candidates = (
        Itinerary(
            (
                Leg(
                    voyage,
                    cargo.route_specification.origin,
                    cargo.route_specification.destination,
                    datetime(2026, 11, 1, tzinfo=UTC),
                    datetime(2026, 11, 2, tzinfo=UTC),
                ),
            )
        ),
    )

    populated = client.get('/admin/cargo/DEF789/itineraries/')
    assert populated.status_code == 200
    assert 'Route option #1' in populated.content.decode()

    routing.candidates = ()
    empty = client.get('/admin/cargo/DEF789/itineraries/')
    assert empty.status_code == 200
    assert 'No routes found' in empty.content.decode()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_assignment_redirects_to_cargo_details_and_result_renders(client):
    call_command('seed_sample_data')
    cargo = repository.find(TrackingId('DEF789'))
    assert cargo is not None
    voyage = DjangoVoyageRepository().find(VoyageNumber('0100S'))
    assert voyage is not None
    candidate = Itinerary(
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
    routing.candidates = (candidate,)

    response = client.post('/admin/cargo/DEF789/route/', {'route_index': '0'})

    assert response.status_code == 302
    assert response.url == '/admin/cargo/DEF789/'
    assert routing.assigned == (TrackingId('DEF789'), candidate)
    details = client.get(response.url)
    details_content = details.content.decode()
    assert details.status_code == 200
    assert 'Routing Details for Cargo DEF789' in details_content
    assert 'Itinerary' in details_content
    assert '0100S' in details_content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
@pytest.mark.parametrize('field_name', ['candidate_index', 'index'])
def test_assignment_accepts_supported_candidate_index_fields(client, field_name):
    call_command('seed_sample_data')
    cargo = repository.find(TrackingId('DEF789'))
    assert cargo is not None
    voyage = DjangoVoyageRepository().find(VoyageNumber('0100S'))
    assert voyage is not None
    candidate = Itinerary(
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
    routing.candidates = (candidate,)

    response = client.post('/admin/cargo/DEF789/itineraries/', {field_name: '0'})

    assert response.status_code == 302
    assert response.url == '/admin/cargo/DEF789/'


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_assignment_rejects_missing_and_out_of_range_candidate_indexes(client):
    call_command('seed_sample_data')
    cargo = repository.find(TrackingId('DEF789'))
    assert cargo is not None
    voyage = DjangoVoyageRepository().find(VoyageNumber('0100S'))
    assert voyage is not None
    routing.candidates = (
        Itinerary(
            (
                Leg(
                    voyage,
                    cargo.route_specification.origin,
                    cargo.route_specification.destination,
                    datetime.now(UTC),
                    datetime.now(UTC) + timedelta(days=1),
                ),
            )
        ),
    )

    missing = client.post('/admin/cargo/DEF789/route/', {})
    out_of_range = client.post('/admin/cargo/DEF789/route/', {'route_index': '1'})
    negative = client.post('/admin/cargo/DEF789/route/', {'route_index': '-1'})
    malformed = client.post('/admin/cargo/DEF789/route/', {'route_index': 'not-a-number'})

    assert missing.status_code == 404
    assert out_of_range.status_code == 404
    assert negative.status_code == 404
    assert malformed.status_code == 404


@pytest.mark.django_db
def test_unknown_cargo_route_selection_preserves_not_found_message():
    with pytest.raises(
        Http404,
        match=r'^Cargo with tracking ID UNKNOWN not found\.$',
    ):
        route_view(
            RequestFactory().get('/admin/cargo/UNKNOWN/route/'),
            'UNKNOWN',
        )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_itinerary_selection_passes_cargo_and_candidates_to_template(client):
    call_command('seed_sample_data')

    response = client.get('/admin/cargo/DEF789/itineraries/')

    assert response.status_code == 200
    assert response.context['cargo'].tracking_id.value == 'DEF789'
    assert response.context['candidates'] == ()
