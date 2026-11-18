from dataclasses import replace
from datetime import UTC, datetime

import pytest
from django.core import signing
from django.core.management import call_command
from django.http import Http404
from django.test import RequestFactory, override_settings
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.routing import CargoRouting
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.booking.interfaces.route_selection.views import create_route_selection_views
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository
from cargotracker.pathfinder.domain.transit_edge import TransitEdge
from cargotracker.pathfinder.domain.transit_path import TransitPath
from cargotracker.voyage.infrastructure.repository import DjangoVoyageRepository

ORIGIN = 'CNHKG'
TRANSFER = 'JNTKO'
DESTINATION = 'AUMEL'


class CandidateRoutingService:
    def __init__(self):
        self.candidates = ()
        self.requested_route = None

    def find_shortest_paths(self, origin, destination):
        self.requested_route = (origin, destination)
        return self.candidates


def _edge(voyage, from_port, to_port, departure_day, arrival_day):
    return TransitEdge(
        voyage,
        from_port,
        to_port,
        datetime(2026, 11, departure_day, tzinfo=UTC),
        datetime(2026, 11, arrival_day, tzinfo=UTC),
    )


def _candidate_paths():
    return (
        TransitPath(
            (
                _edge('0300A', ORIGIN, TRANSFER, 8, 9),
                _edge('0200T', TRANSFER, DESTINATION, 10, 11),
            )
        ),
        TransitPath(
            (
                _edge('0100S', ORIGIN, 'SESTO', 12, 13),
                _edge('0400S', 'SESTO', DESTINATION, 14, 15),
            )
        ),
    )


candidate_routing_service = CandidateRoutingService()
cargo_repository = DjangoCargoRepository()
cargo_dashboard = CargoDashboard(cargo_repository)
route_view, select_itinerary_view = create_route_selection_views(
    CargoRouting(
        cargo_repository,
        DjangoLocationRepository(),
        DjangoVoyageRepository(),
        DjangoHandlingEventRepository(),
        candidate_routing_service,
    ),
    cargo_dashboard,
)
_, cargo_details_view = create_booking_views(cargo_dashboard)
urlpatterns = [
    path('admin/cargo/<str:tracking_id>/route/', route_view),
    path('admin/cargo/<str:tracking_id>/itineraries/', select_itinerary_view),
    path('admin/cargo/<str:tracking_id>/', cargo_details_view),
]


@pytest.fixture(autouse=True)
def reset_candidate_routing():
    candidate_routing_service.candidates = ()
    candidate_routing_service.requested_route = None


@pytest.fixture
def seeded_route_candidates(monkeypatch):
    now = datetime(2026, 11, 7, tzinfo=UTC)
    monkeypatch.setattr(
        'cargotracker.cargo.management.commands.seed_sample_data.timezone.now', lambda: now
    )
    call_command('seed_sample_data')
    candidate_routing_service.candidates = _candidate_paths()
    return cargo_repository.find(TrackingId('DEF789'))


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_page_displays_candidate_count_and_numbered_itinerary_legs(
    client, seeded_route_candidates
):
    response = client.get('/admin/cargo/DEF789/route/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Routing Details for Cargo DEF789' in content
    assert 'Potential routes:' in content
    assert 'aria-live="polite">2</span>' in content
    assert 'Itinerary 1' in content and 'Itinerary 2' in content
    assert 'Leg 1' in content and 'Leg 2' in content
    assert '0300A' in content and '0200T' in content
    assert 'role="alert"' not in content
    assert response.context['candidate_error'] == ''

    candidates = [route['itinerary'] for route in response.context['routes']]
    assert candidate_routing_service.requested_route == (ORIGIN, DESTINATION)
    assert candidates
    assert all(candidate.legs for candidate in candidates)
    assert all(
        candidate.legs[0].load_location == seeded_route_candidates.route_specification.origin
        for candidate in candidates
    )
    assert all(
        candidate.legs[-1].unload_location
        == seeded_route_candidates.route_specification.destination
        for candidate in candidates
    )
    assert all(
        first.unload_location == second.load_location
        for candidate in candidates
        for first, second in zip(candidate.legs, candidate.legs[1:])
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_assigning_candidate_redirects_to_details_and_persists_that_itinerary(
    client, seeded_route_candidates
):
    response = client.get('/admin/cargo/DEF789/route/')
    selected_itinerary = response.context['routes'][1]['itinerary']
    candidate_token = response.context['routes'][1]['token']

    assigned_response = client.post(
        '/admin/cargo/DEF789/route/',
        {'candidate': candidate_token},
        follow=True,
    )
    assigned_cargo = cargo_repository.find(TrackingId('DEF789'))

    assert assigned_response.redirect_chain == [('/admin/cargo/DEF789/', 302)]
    assert assigned_response.status_code == 200
    assert 'Routing Details for Cargo DEF789' in assigned_response.content.decode()
    assert '0400S' in assigned_response.content.decode()
    assert assigned_cargo is not None
    assert assigned_cargo.itinerary == selected_itinerary


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_select_itinerary_renders_populated_candidates(seeded_route_candidates, client):
    response = client.get('/admin/cargo/DEF789/itineraries/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Select an Itinerary for Cargo DEF789' in content
    assert 'Potential routes:' in content
    assert 'Itinerary 1' in content and 'Itinerary 2' in content
    assert 'No routes found' not in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_and_select_itinerary_show_no_route_guidance(seeded_route_candidates, client):
    candidate_routing_service.candidates = ()

    route_response = client.get('/admin/cargo/DEF789/route/')
    selection_response = client.get('/admin/cargo/DEF789/itineraries/')

    assert 'Potential routes:' in route_response.content.decode()
    assert '0</span>' in route_response.content.decode()
    assert (
        'No routes found that satisfy the route specification. '
        'Try setting an arrival deadline further into the future.'
        in route_response.content.decode()
    )
    assert (
        'No routes found that satisfy the route specification. '
        'Try setting an arrival deadline further into the future (a few weeks at least).'
        in selection_response.content.decode()
    )
    assert 'Assign itinerary' not in selection_response.content.decode()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_invalid_candidate_token_does_not_assign_a_route(client, seeded_route_candidates):
    response = client.get('/admin/cargo/DEF789/route/')
    token = response.context['routes'][0]['token']
    tampered_token = f'X{token[1:]}'

    assignment_response = client.post(
        '/admin/cargo/DEF789/route/',
        {'candidate': tampered_token},
    )
    cargo = cargo_repository.find(TrackingId('DEF789'))

    assert assignment_response.status_code == 400
    assert assignment_response.context['candidate_error'] == 'Choose a valid route.'
    assert cargo is not None
    assert not cargo.itinerary.legs


@pytest.mark.parametrize(
    'url',
    ['/admin/cargo/DEF789/route/', '/admin/cargo/DEF789/itineraries/'],
)
@override_settings(ROOT_URLCONF=__name__)
def test_route_pages_reject_unsupported_methods(client, url):
    response = client.put(url)

    assert response.status_code == 405
    assert response.headers['Allow'] == 'GET, POST'


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_page_reports_missing_cargo():
    with pytest.raises(Http404, match=r'^Cargo with tracking ID UNKNOWN not found\.$'):
        route_view(RequestFactory().get('/admin/cargo/UNKNOWN/route/'), 'UNKNOWN')


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_signed_candidate_for_another_cargo_cannot_be_assigned(client, seeded_route_candidates):
    response = client.get('/admin/cargo/DEF789/route/')
    token = response.context['routes'][0]['token']

    assignment_response = client.post(
        '/admin/cargo/MNO456/route/',
        {'candidate': token},
    )

    assert assignment_response.status_code == 400
    assert assignment_response.context['candidate_error'] == 'Choose a valid route.'


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
@pytest.mark.parametrize(
    'payload',
    [
        ['not a mapping'],
        {'tracking_id': 'DEF789', 'legs': []},
    ],
)
def test_invalid_signed_candidate_payloads_are_rejected(client, seeded_route_candidates, payload):
    token = signing.dumps(payload, salt='booking.route-selection')

    response = client.post('/admin/cargo/DEF789/route/', {'candidate': token})

    assert response.status_code == 400
    assert response.context['candidate_error'] == 'Choose a valid route.'


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_missing_candidate_is_rejected(client, seeded_route_candidates):
    response = client.post('/admin/cargo/DEF789/route/')

    assert response.status_code == 400
    assert response.context['candidate_error'] == 'Choose a valid route.'


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_candidate_must_still_satisfy_the_current_route_specification(
    client, seeded_route_candidates
):
    response = client.get('/admin/cargo/DEF789/route/')
    token = response.context['routes'][1]['token']
    updated_specification = replace(
        seeded_route_candidates.route_specification,
        arrival_deadline=datetime(2026, 11, 14, tzinfo=UTC),
    )
    cargo_repository.upsert(
        replace(seeded_route_candidates, route_specification=updated_specification)
    )

    assignment_response = client.post(
        '/admin/cargo/DEF789/route/',
        {'candidate': token},
    )
    cargo = cargo_repository.find(TrackingId('DEF789'))

    assert assignment_response.status_code == 400
    assert (
        assignment_response.context['candidate_error']
        == 'Choose a route that satisfies the current route specification.'
    )
    assert cargo is not None
    assert not cargo.itinerary.legs
