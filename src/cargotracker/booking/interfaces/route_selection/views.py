from collections.abc import Callable
from datetime import datetime

from django.core import signing
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.routing import CargoRouting
from cargotracker.cargo.domain.cargo import Cargo
from cargotracker.cargo.domain.itinerary import Itinerary
from cargotracker.cargo.domain.leg import Leg
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location
from cargotracker.location.domain.un_locode import UnLocode
from cargotracker.voyage.domain.schedule import Schedule
from cargotracker.voyage.domain.voyage import Voyage
from cargotracker.voyage.domain.voyage_number import VoyageNumber

_ITINERARY_SALT = 'cargotracker.booking.route-selection'


def create_route_selection_views(
    cargo_routing: CargoRouting,
    cargo_dashboard: CargoDashboard,
) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
    def route_selection(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = _get_cargo(cargo_dashboard, tracking_id)
        if request.method == 'POST':
            try:
                itinerary = _decode_itinerary(
                    request.POST['itinerary_token'],
                    cargo.tracking_id,
                )
            except (signing.BadSignature, KeyError, TypeError, ValueError):
                return _render_route_selection(
                    request,
                    cargo_routing,
                    cargo,
                    title='Route Cargo',
                    no_routes_guidance=('Try setting an arrival deadline further into the future.'),
                    error='Select a route shown on this page.',
                    status=400,
                )
            cargo_routing.assign_route(cargo.tracking_id, itinerary)
            return redirect(f'/admin/cargo/{cargo.tracking_id.value}/')
        return _render_route_selection(
            request,
            cargo_routing,
            cargo,
            title='Route Cargo',
            no_routes_guidance='Try setting an arrival deadline further into the future.',
        )

    def select_itinerary(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = _get_cargo(cargo_dashboard, tracking_id)
        return _render_route_selection(
            request,
            cargo_routing,
            cargo,
            title='Select Itinerary',
            no_routes_guidance=(
                'Try setting an arrival deadline further into the future (a few weeks at least).'
            ),
        )

    return route_selection, select_itinerary


def _get_cargo(cargo_dashboard: CargoDashboard, tracking_id: str) -> Cargo:
    cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
    if cargo is None:
        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
    return cargo


def _render_route_selection(
    request: HttpRequest,
    cargo_routing: CargoRouting,
    cargo: Cargo,
    *,
    title: str,
    no_routes_guidance: str,
    error: str | None = None,
    status: int = 200,
) -> HttpResponse:
    routes = [
        {
            'itinerary': itinerary,
            'token': signing.dumps(
                {
                    'tracking_id': cargo.tracking_id.value,
                    'legs': [_encode_leg(leg) for leg in itinerary.legs],
                },
                salt=_ITINERARY_SALT,
            ),
        }
        for itinerary in cargo_routing.route_candidates(cargo.tracking_id)
    ]
    return render(
        request,
        'booking/route_selection/route_selection.html',
        {
            'cargo': cargo,
            'routes': routes,
            'title': title,
            'no_routes_guidance': no_routes_guidance,
            'error': error,
        },
        status=status,
    )


def _encode_leg(leg: Leg) -> dict[str, str]:
    return {
        'voyage_number': leg.voyage.voyage_number.value,
        'load_unlocode': leg.load_location.unlocode.value,
        'load_name': leg.load_location.name,
        'unload_unlocode': leg.unload_location.unlocode.value,
        'unload_name': leg.unload_location.name,
        'load_time': leg.load_time.isoformat(),
        'unload_time': leg.unload_time.isoformat(),
    }


def _decode_itinerary(token: str, tracking_id: TrackingId) -> Itinerary:
    payload = signing.loads(token, salt=_ITINERARY_SALT)
    if not isinstance(payload, dict) or payload.get('tracking_id') != tracking_id.value:
        raise ValueError
    legs = payload.get('legs')
    if not isinstance(legs, list) or not legs:
        raise ValueError
    return Itinerary(
        tuple(
            Leg(
                Voyage(VoyageNumber(leg['voyage_number']), Schedule.EMPTY),
                Location(UnLocode(leg['load_unlocode']), leg['load_name']),
                Location(UnLocode(leg['unload_unlocode']), leg['unload_name']),
                datetime.fromisoformat(leg['load_time']),
                datetime.fromisoformat(leg['unload_time']),
            )
            for leg in legs
        )
    )
