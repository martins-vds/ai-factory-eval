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


class CandidateRoutingService:
    candidates = ()

    def find_shortest_paths(self, origin, destination):
        return ()


candidates_service = CandidateRoutingService()
cargo_routing = CargoRouting(
    DjangoCargoRepository(),
    DjangoLocationRepository(),
    DjangoVoyageRepository(),
    DjangoHandlingEventRepository(),
    candidates_service,
)
route_selection_view, itinerary_selection_view, assign_route_view = create_route_selection_views(
    cargo_routing
)
_, cargo_details_view = create_booking_views(CargoDashboard(DjangoCargoRepository()))
urlpatterns = [
    path('admin/cargo/<str:tracking_id>/', cargo_details_view),
    path('admin/cargo/<str:tracking_id>/route/', route_selection_view),
    path(
        'admin/cargo/<str:tracking_id>/itineraries/',
        itinerary_selection_view,
    ),
    path(
        'admin/cargo/<str:tracking_id>/route/assign/',
        assign_route_view,
    ),
]


@pytest.fixture(autouse=True)
def reset_candidates(monkeypatch):
    monkeypatch.setattr(candidates_service, 'candidates', (), raising=False)
    monkeypatch.setattr(
        candidates_service,
        'find_shortest_paths',
        lambda origin, destination: candidates_service.candidates,
    )
    monkeypatch.setattr(
        cargo_routing,
        'route_candidates',
        lambda tracking_id: candidates_service.candidates,
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_selection_renders_populated_numbered_candidates(client, monkeypatch):
    call_command('seed_sample_data')
    cargo = DjangoCargoRepository().find(TrackingId('DEF789'))
    assert cargo is not None
    voyage = DjangoVoyageRepository().find(VoyageNumber('0100S'))
    assert voyage is not None
    itinerary = Itinerary(
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
    monkeypatch.setattr(candidates_service, 'candidates', (itinerary,))

    response = client.get('/admin/cargo/DEF789/route/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Hong Kong' in content
    assert 'Melbourne' in content
    assert 'Candidate routes:' in content
    assert '1' in content
    assert '0100S' in content
    assert 'CNHKG' in content
    assert 'AUMEL' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_selection_renders_empty_candidate_guidance(client):
    call_command('seed_sample_data')

    response = client.get('/admin/cargo/DEF789/route/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Candidate routes: 0' in content
    assert 'No routes found that satisfy the route specification.' in content
    assert 'Try setting an arrival deadline further into the future.' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_itinerary_selection_renders_candidates_when_present(client, monkeypatch):
    call_command('seed_sample_data')
    cargo = DjangoCargoRepository().find(TrackingId('DEF789'))
    assert cargo is not None
    voyage = DjangoVoyageRepository().find(VoyageNumber('0100S'))
    assert voyage is not None
    itinerary = Itinerary(
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
    monkeypatch.setattr(candidates_service, 'candidates', (itinerary,))

    response = client.get('/admin/cargo/DEF789/itineraries/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Candidate routes: 1' in content
    assert 'Candidate 1' in content
    assert '0100S' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_candidate_assignment_redirects_to_resulting_cargo_details(client):
    call_command('seed_sample_data')
    cargo = DjangoCargoRepository().find(TrackingId('DEF789'))
    assert cargo is not None
    voyage = DjangoVoyageRepository().find(VoyageNumber('0100S'))
    assert voyage is not None
    itinerary = Itinerary(
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
    candidates_service.candidates = (itinerary,)

    response = client.post(
        '/admin/cargo/DEF789/route/assign/',
        {'candidate': '0'},
    )

    assert response.status_code == 302
    assert response.url == '/admin/cargo/DEF789/'
    details = client.get(response.url)
    assert details.status_code == 200
    assert '0100S' in details.content.decode()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_unknown_cargo_route_selection_and_itinerary_selection_return_404(client):
    route_response = client.get('/admin/cargo/UNKNOWN/route/')
    itinerary_response = client.get('/admin/cargo/UNKNOWN/itineraries/')

    assert route_response.status_code == 404
    assert itinerary_response.status_code == 404


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_assignment_get_redirects_to_route_selection(client):
    call_command('seed_sample_data')

    response = client.get('/admin/cargo/DEF789/route/assign/')

    assert response.status_code == 302
    assert response.url == '/admin/cargo/DEF789/route/'


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
@pytest.mark.parametrize('candidate', ['', '-1', '1'])
def test_assignment_rejects_missing_or_out_of_range_candidate(client, candidate):
    call_command('seed_sample_data')

    response = client.post(
        '/admin/cargo/DEF789/route/assign/',
        {'candidate': candidate},
    )

    assert response.status_code == 404


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_assignment_rejects_index_equal_to_candidate_count_with_exact_error():
    call_command('seed_sample_data')
    cargo = DjangoCargoRepository().find(TrackingId('DEF789'))
    assert cargo is not None
    voyage = DjangoVoyageRepository().find(VoyageNumber('0100S'))
    assert voyage is not None
    itinerary = Itinerary(
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
    candidates_service.candidates = (itinerary,)
    request = RequestFactory().post('/admin/cargo/DEF789/route/assign/', {'candidate': '1'})

    with pytest.raises(Http404, match=r'^No route candidate was selected\.$'):
        assign_route_view(request, 'DEF789')


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_unknown_cargo_raises_the_existing_not_found_error():
    request = RequestFactory().get('/admin/cargo/UNKNOWN/route/')

    with pytest.raises(Http404, match=r'^Cargo with tracking ID UNKNOWN not found\.$'):
        route_selection_view(request, 'UNKNOWN')


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_optional_cargo_dashboard_lookup_renders_route_details(client):
    call_command('seed_sample_data')
    dashboard_routing_view, _, _ = create_route_selection_views(
        cargo_routing,
        CargoDashboard(DjangoCargoRepository()),
    )
    request = RequestFactory().get('/admin/cargo/DEF789/route/')

    response = dashboard_routing_view(request, 'DEF789')

    assert response.status_code == 200
