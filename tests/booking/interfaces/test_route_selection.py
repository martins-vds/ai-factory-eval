import re
from datetime import UTC, datetime, timedelta
from itertools import pairwise

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.registration import CargoRegistration
from cargotracker.booking.application.routing import CargoRouting
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.booking.interfaces.route_selection.views import create_route_selection_views
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.domain.un_locode import UnLocode
from cargotracker.location.infrastructure.repository import DjangoLocationRepository
from cargotracker.pathfinder.application.routing import SAMPLE_VOYAGE_NUMBERS, RoutingService
from cargotracker.voyage.infrastructure.repository import DjangoVoyageRepository

cargo_repository = DjangoCargoRepository()
route_service = RoutingService()
cargo_routing = CargoRouting(
    cargo_repository,
    DjangoLocationRepository(),
    DjangoVoyageRepository(),
    DjangoHandlingEventRepository(),
    route_service,
)
cargo_dashboard = CargoDashboard(cargo_repository)
route_view, select_itinerary_view = create_route_selection_views(cargo_routing, cargo_dashboard)
dashboard_view, cargo_details_view = create_booking_views(cargo_dashboard)
urlpatterns = [
    path('admin/dashboard/', dashboard_view),
    path('admin/cargo/<str:tracking_id>/', cargo_details_view),
    path('admin/cargo/<str:tracking_id>/route/', route_view),
    path('admin/cargo/<str:tracking_id>/itineraries/', select_itinerary_view),
]


@pytest.fixture
def not_routed_cargo():
    call_command('seed_sample_data')
    locations = DjangoLocationRepository()
    origin = locations.find(UnLocode('USNYC'))
    destination = locations.find(UnLocode('FIHEL'))
    assert origin is not None
    assert destination is not None

    return CargoRegistration(cargo_repository).register(
        origin,
        destination,
        datetime.now(UTC) + timedelta(days=365 * 5),
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_page_renders_candidate_properties_and_numbered_legs(client, not_routed_cargo):
    response = client.get(f'/admin/cargo/{not_routed_cargo}/route/')
    content = response.content.decode()
    candidates = [candidate['itinerary'] for candidate in response.context['route_candidates']]

    assert response.status_code == 200
    assert response.context['cargo'].tracking_id.value == str(not_routed_cargo)
    assert 3 <= len(candidates) <= 5
    assert 'Origin:' in content
    assert 'New York' in content
    assert 'USNYC' in content
    assert 'Destination:' in content
    assert 'Helsinki' in content
    assert 'FIHEL' in content
    assert 'Arrival deadline:' in content
    assert f'Potential routes: {len(candidates)}' in content
    assert 'Itinerary 1' in content

    for itinerary in candidates:
        assert itinerary.legs[0].load_location.unlocode.value == 'USNYC'
        assert itinerary.legs[-1].unload_location.unlocode.value == 'FIHEL'
        assert all(
            previous.unload_location == following.load_location
            for previous, following in pairwise(itinerary.legs)
        )
        assert all(
            leg.load_time < leg.unload_time
            and leg.voyage.voyage_number.value in SAMPLE_VOYAGE_NUMBERS
            for leg in itinerary.legs
        )
        assert all(
            previous.unload_time < following.load_time
            for previous, following in pairwise(itinerary.legs)
        )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_select_itinerary_renders_candidates_when_present(client, not_routed_cargo):
    response = client.get(f'/admin/cargo/{not_routed_cargo}/itineraries/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Select Itinerary for Cargo' in content
    assert 'Potential routes:' in content
    assert 'Itinerary 1' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_select_itinerary_keeps_no_routes_guidance_when_candidates_are_empty(
    client, not_routed_cargo, monkeypatch
):
    monkeypatch.setattr(route_service, 'find_shortest_paths', lambda origin, destination: ())

    response = client.get(f'/admin/cargo/{not_routed_cargo}/itineraries/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'No routes found that satisfy the route specification.' in content
    assert 'Try setting an arrival deadline further into the future' in re.sub(r'\s+', ' ', content)
    assert 'Itinerary 1' not in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_selection_unknown_cargo_returns_http_404(client):
    response = client.get('/admin/cargo/UNKNOWN/route/')

    assert response.status_code == 404


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_selection_rejects_methods_other_than_get_and_post(client, not_routed_cargo):
    response = client.put(f'/admin/cargo/{not_routed_cargo}/route/')

    assert response.status_code == 405
    assert response.headers['Allow'] == 'GET, POST'


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_assigning_candidate_redirects_to_cargo_details_and_persists_selected_route(
    client, not_routed_cargo, monkeypatch
):
    calls = []
    find_shortest_paths = route_service.find_shortest_paths

    def find_paths(origin, destination):
        calls.append((origin, destination))
        return find_shortest_paths(origin, destination)

    monkeypatch.setattr(route_service, 'find_shortest_paths', find_paths)
    route_url = f'/admin/cargo/{not_routed_cargo}/route/'
    route_page = client.get(route_url)
    selected_itinerary = route_page.context['route_candidates'][0]['itinerary']
    token = re.search(rb'name="route_token" value="([^"]+)"', route_page.content)
    assert token is not None

    response = client.post(route_url, {'route_token': token.group(1).decode()}, follow=True)
    content = response.content.decode()
    stored_cargo = cargo_repository.find(TrackingId(str(not_routed_cargo)))

    assert response.status_code == 200
    assert response.redirect_chain == [(f'/admin/cargo/{not_routed_cargo}/', 302)]
    assert 'Routing Details for Cargo' in content
    assert all(leg.voyage.voyage_number.value in content for leg in selected_itinerary.legs)
    assert stored_cargo is not None
    assert stored_cargo.itinerary == selected_itinerary
    assert len(calls) == 1


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
@pytest.mark.parametrize('route_token', (None, '', 'not-a-signed-route'))
def test_invalid_route_selection_token_is_rejected_without_assignment(
    client, not_routed_cargo, route_token
):
    data = {} if route_token is None else {'route_token': route_token}
    response = client.post(f'/admin/cargo/{not_routed_cargo}/route/', data)
    stored_cargo = cargo_repository.find(TrackingId(str(not_routed_cargo)))

    assert response.status_code == 400
    assert response.content == b'Invalid route selection.'
    assert stored_cargo is not None
    assert not stored_cargo.itinerary.legs


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_selection_token_cannot_be_submitted_for_another_cargo(client, not_routed_cargo):
    route_page = client.get(f'/admin/cargo/{not_routed_cargo}/route/')
    token = re.search(rb'name="route_token" value="([^"]+)"', route_page.content)
    assert token is not None

    response = client.post(
        '/admin/cargo/OTHER/route/',
        {'route_token': token.group(1).decode()},
    )

    assert response.status_code == 400
