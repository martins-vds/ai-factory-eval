import random
from datetime import UTC, datetime, timedelta

import pytest
from django.core.management import call_command
from django.urls import path
from django.test import override_settings

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.registration import CargoRegistration
from cargotracker.booking.application.routing import CargoRouting
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.booking.interfaces.route_selection.views import (
    create_route_selection_views,
)
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.domain.un_locode import UnLocode
from cargotracker.location.infrastructure.repository import DjangoLocationRepository
from cargotracker.pathfinder.application.routing import RoutingService
from cargotracker.voyage.infrastructure.repository import DjangoVoyageRepository

ROUTING_NOW = datetime(2026, 11, 7, tzinfo=UTC)
cargo_repository = DjangoCargoRepository()
location_repository = DjangoLocationRepository()
cargo_dashboard = CargoDashboard(cargo_repository)
cargo_routing = CargoRouting(
    cargo_repository,
    location_repository,
    DjangoVoyageRepository(),
    DjangoHandlingEventRepository(),
    RoutingService(random.Random(0), lambda: ROUTING_NOW),
)
route_view, select_itinerary_view = create_route_selection_views(cargo_dashboard, cargo_routing)
_, cargo_details_view = create_booking_views(cargo_dashboard)
urlpatterns = [
    path('admin/cargo/<str:tracking_id>/route/', route_view),
    path('admin/cargo/<str:tracking_id>/itineraries/', select_itinerary_view),
    path('admin/cargo/<str:tracking_id>/', cargo_details_view),
]


@pytest.fixture
def register_cargo(db):
    call_command('seed_sample_data')
    origin = location_repository.find(UnLocode('CNHKG'))
    destination = location_repository.find(UnLocode('AUMEL'))
    assert origin is not None
    assert destination is not None

    def register(deadline):
        return CargoRegistration(cargo_repository).register(origin, destination, deadline).value

    return register


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_page_displays_cargo_and_candidate_properties(client, register_cargo):
    tracking_id = register_cargo(datetime(2030, 1, 1, tzinfo=UTC))

    response = client.get(f'/admin/cargo/{tracking_id}/route/')
    content = response.content.decode()
    cargo = response.context['cargo']
    candidates = response.context['candidates']

    assert response.status_code == 200
    assert 'Origin:' in content
    assert 'Hong Kong' in content
    assert 'CNHKG' in content
    assert 'Destination:' in content
    assert 'Melbourne' in content
    assert 'AUMEL' in content
    assert 'Arrival deadline:' in content
    assert f'Potential routes: {len(candidates)}' in content
    assert candidates

    for candidate_index, itinerary in enumerate(candidates, start=1):
        assert itinerary.legs
        assert itinerary.legs[0].load_location == cargo.route_specification.origin
        assert itinerary.legs[-1].unload_location == cargo.route_specification.destination
        assert f'Route option #{candidate_index}' in content
        for leg_index, leg in enumerate(itinerary.legs, start=1):
            assert f'Leg {leg_index}' in content
            assert leg.voyage.voyage_number.value in content
            assert leg.load_location.name in content
            assert leg.load_location.unlocode.value in content
            assert leg.load_time.strftime('%m/%d/%Y') in content
            assert leg.unload_location.name in content
            assert leg.unload_location.unlocode.value in content
            assert leg.unload_time.strftime('%m/%d/%Y') in content
        assert all(
            previous.unload_location == following.load_location
            for previous, following in zip(itinerary.legs, itinerary.legs[1:])
        )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_select_itinerary_renders_populated_candidates(client, register_cargo):
    tracking_id = register_cargo(datetime(2030, 1, 1, tzinfo=UTC))

    response = client.get(f'/admin/cargo/{tracking_id}/itineraries/')
    content = response.content.decode()

    assert response.status_code == 200
    assert response.context['candidates']
    assert 'Potential routes:' in content
    assert 'Route option #1' in content
    assert 'name="route_index"' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_route_and_select_itinerary_show_no_route_guidance(client, register_cargo):
    tracking_id = register_cargo(ROUTING_NOW - timedelta(days=1))

    route_response = client.get(f'/admin/cargo/{tracking_id}/route/')
    itinerary_response = client.get(f'/admin/cargo/{tracking_id}/itineraries/')

    assert route_response.status_code == 200
    assert route_response.context['candidates'] == ()
    assert (
        'No routes found that satisfy the route specification. '
        'Try setting an arrival deadline further into the future.'
    ) in route_response.content.decode()
    assert itinerary_response.status_code == 200
    assert itinerary_response.context['candidates'] == ()
    assert 'Try setting an arrival deadline further into the future (a few weeks at least).' in (
        itinerary_response.content.decode()
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_assign_candidate_redirects_to_cargo_details(client, monkeypatch, register_cargo):
    tracking_id = register_cargo(datetime(2030, 1, 1, tzinfo=UTC))
    candidates = cargo_routing.route_candidates(TrackingId(tracking_id))
    assert len(candidates) > 1
    monkeypatch.setattr(cargo_routing, 'route_candidates', lambda _tracking_id: candidates)
    selected_index = 1
    selected_candidate = candidates[selected_index]

    response = client.post(
        f'/admin/cargo/{tracking_id}/route/',
        {'route_index': str(selected_index)},
    )
    details_response = client.get(response.url)
    cargo = cargo_repository.find(TrackingId(tracking_id))

    assert response.status_code == 302
    assert response.url == f'/admin/cargo/{tracking_id}/'
    assert details_response.status_code == 200
    assert cargo is not None
    assert cargo.itinerary == selected_candidate
    details_content = details_response.content.decode()
    assert 'Routing Details for Cargo' in details_content
    assert 'Itinerary' in details_content
    assert selected_candidate.legs[0].voyage.voyage_number.value in details_content
