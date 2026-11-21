from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from django.http import Http404
from django.test import RequestFactory

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.booking.interfaces.route_selection.views import (
    create_route_selection_views,
    create_route_selection_view,
)
from cargotracker.cargo.domain.itinerary import Itinerary
from cargotracker.cargo.domain.tracking_id import TrackingId


class RouteCargoDashboard:
    def __init__(self, cargo):
        self.cargo = cargo

    def find(self, tracking_id):
        return self.cargo

    def get_cargo_details(self, tracking_id):
        return self.cargo


class RouteRouting:
    def __init__(self, cargo, candidates):
        self.cargo = cargo
        self.candidates = candidates
        self.assigned = None

    def route_candidates(self, tracking_id):
        assert isinstance(tracking_id, TrackingId)
        return tuple(self.candidates)

    def assign_route(self, tracking_id, itinerary):
        assert isinstance(tracking_id, TrackingId)
        self.assigned = (tracking_id, itinerary)
        self.cargo.itinerary = itinerary
        return self.cargo

    def _find_cargo(self, tracking_id):
        assert isinstance(tracking_id, TrackingId)
        return self.cargo


def candidate():
    origin = SimpleNamespace(name='Hong Kong', unlocode=SimpleNamespace(value='CNHKG'))
    transfer = SimpleNamespace(name='Tokyo', unlocode=SimpleNamespace(value='JNTKO'))
    destination = SimpleNamespace(name='Melbourne', unlocode=SimpleNamespace(value='AUMEL'))
    voyage = SimpleNamespace(voyage_number=SimpleNamespace(value='0300A'))
    legs = (
        SimpleNamespace(
            voyage=voyage,
            load_location=origin,
            unload_location=transfer,
            load_time=datetime(2026, 10, 1, tzinfo=UTC),
            unload_time=datetime(2026, 10, 2, tzinfo=UTC),
        ),
        SimpleNamespace(
            voyage=voyage,
            load_location=transfer,
            unload_location=destination,
            load_time=datetime(2026, 10, 3, tzinfo=UTC),
            unload_time=datetime(2026, 10, 4, tzinfo=UTC),
        ),
    )
    return SimpleNamespace(legs=legs)


def cargo(candidates):
    origin = SimpleNamespace(name='Hong Kong', unlocode=SimpleNamespace(value='CNHKG'))
    destination = SimpleNamespace(name='Melbourne', unlocode=SimpleNamespace(value='AUMEL'))
    return SimpleNamespace(
        tracking_id=SimpleNamespace(value='DEF789'),
        route_specification=SimpleNamespace(
            origin=origin,
            destination=destination,
            arrival_deadline=datetime(2026, 11, 1, tzinfo=UTC),
        ),
        itinerary=Itinerary.EMPTY,
        delivery=SimpleNamespace(misdirected=False),
    )


@pytest.fixture
def route_views():
    candidate_itinerary = candidate()
    cargo_object = cargo((candidate_itinerary,))
    routing = RouteRouting(cargo_object, (candidate_itinerary,))
    route_view, itinerary_view = create_route_selection_views(
        routing,
        RouteCargoDashboard(cargo_object),
    )
    return route_view, itinerary_view, routing, cargo_object


def test_populated_route_selection_displays_candidates(route_views):
    route_view, _, _, _ = route_views

    response = route_view(RequestFactory().get('/admin/cargo/DEF789/route/'), 'DEF789')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Set Route for Cargo DEF789' in content
    assert 'Potential routes:' in content
    assert '<dd>1</dd>' in content
    assert 'Potential routes:' in content
    assert 'Route option #1' in content
    assert 'Hong Kong' in content
    assert 'Tokyo' in content
    assert 'Melbourne' in content
    assert '0300A' in content
    assert 'Select' in content


def test_empty_route_selection_shows_no_route_guidance():
    cargo_object = cargo(())
    routing = RouteRouting(cargo_object, ())
    route_view, itinerary_view = create_route_selection_views(
        routing,
        RouteCargoDashboard(cargo_object),
    )

    response = route_view(RequestFactory().get('/admin/cargo/DEF789/route/'), 'DEF789')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Potential routes:' in content
    assert 'No routes found that satisfy the route specification' in content
    assert 'Try setting an arrival deadline further into the future' in content
    assert itinerary_view is not None


def test_candidate_assignment_redirects_to_cargo_details(route_views):
    _, _, routing, cargo_object = route_views
    _, itinerary_view = create_route_selection_views(
        routing,
        RouteCargoDashboard(cargo_object),
    )

    response = itinerary_view(
        RequestFactory().post(
            '/admin/cargo/DEF789/itineraries/',
            {'candidate': '0'},
        ),
        'DEF789',
    )

    assert response.status_code == 302
    assert response.url == '/admin/cargo/DEF789/'


def test_itinerary_selection_renders_candidates_and_resulting_details_page(route_views):
    _, itinerary_view, _, cargo_object = route_views

    selection_response = itinerary_view(
        RequestFactory().get('/admin/cargo/DEF789/itineraries/'),
        'DEF789',
    )
    assert selection_response.status_code == 200
    assert 'Select an itinerary for Cargo DEF789' in selection_response.content.decode()
    assert 'Route option #1' in selection_response.content.decode()

    assignment_response = itinerary_view(
        RequestFactory().post(
            '/admin/cargo/DEF789/itineraries/',
            {'candidate': '0'},
        ),
        'DEF789',
    )
    assert assignment_response.url == '/admin/cargo/DEF789/'

    _, cargo_details_view = create_booking_views(CargoDashboard(RouteCargoDashboard(cargo_object)))
    details_response = cargo_details_view(
        RequestFactory().get('/admin/cargo/DEF789/'),
        'DEF789',
    )
    details = details_response.content.decode()

    assert details_response.status_code == 200
    assert 'Routing Details for Cargo DEF789' in details
    assert 'Itinerary' in details
    assert '0300A' in details


@pytest.mark.parametrize('candidate', ['', '-1', '1', 'not-a-number'])
def test_invalid_candidate_selection_is_rejected(candidate, route_views):
    _, itinerary_view, _, _ = route_views

    with pytest.raises(Http404, match='A valid route candidate is required'):
        itinerary_view(
            RequestFactory().post(
                '/admin/cargo/DEF789/itineraries/',
                {'candidate': candidate},
            ),
            'DEF789',
        )


def test_route_factory_alias_and_fallback_cargo_lookup(route_views):
    _, _, routing, cargo_object = route_views

    assert create_route_selection_view is create_route_selection_views
    route_view, _ = create_route_selection_views(routing)
    response = route_view(
        RequestFactory().get('/admin/cargo/DEF789/route/'),
        'DEF789',
    )

    assert response.status_code == 200
    assert cargo_object.tracking_id.value in response.content.decode()


def test_unknown_cargo_route_returns_not_found_error():
    class MissingCargoDashboard:
        def get_cargo_details(self, tracking_id):
            assert isinstance(tracking_id, TrackingId)
            return None

    routing = RouteRouting(None, ())
    route_view, _ = create_route_selection_views(routing, MissingCargoDashboard())

    with pytest.raises(
        Http404,
        match=r'^Cargo with tracking ID UNKNOWN not found\.$',
    ):
        route_view(
            RequestFactory().get('/admin/cargo/UNKNOWN/route/'),
            'UNKNOWN',
        )
