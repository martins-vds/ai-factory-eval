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
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.location.domain.un_locode import UnLocode
from cargotracker.location.infrastructure.repository import DjangoLocationRepository
from cargotracker.pathfinder.application.routing import SAMPLE_VOYAGE_NUMBERS, RoutingService
from cargotracker.voyage.infrastructure.repository import DjangoVoyageRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository

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
    assert 3 <= len(candidates) <= 5
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
