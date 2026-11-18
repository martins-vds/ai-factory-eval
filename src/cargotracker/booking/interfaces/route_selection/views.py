from collections.abc import Callable
from datetime import datetime

from django.core import signing
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import redirect, render

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.routing import CargoRouting
from cargotracker.cargo.domain.itinerary import Itinerary
from cargotracker.cargo.domain.leg import Leg
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location
from cargotracker.location.domain.un_locode import UnLocode
from cargotracker.voyage.domain.schedule import Schedule
from cargotracker.voyage.domain.voyage import Voyage
from cargotracker.voyage.domain.voyage_number import VoyageNumber

_ROUTE_SELECTION_SALT = 'cargotracker.booking.route-selection'

def create_route_selection_views(
    cargo_routing: CargoRouting,
    cargo_dashboard: CargoDashboard,
) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
    def route_selection(request: HttpRequest, tracking_id: str) -> HttpResponse:
        return _render_route_selection(
            request,
            tracking_id,
            cargo_routing,
            cargo_dashboard,
            'booking/route_selection/route.html',
        )

    def select_itinerary(request: HttpRequest, tracking_id: str) -> HttpResponse:
        return _render_route_selection(
            request,
            tracking_id,
            cargo_routing,
            cargo_dashboard,
            'booking/route_selection/select_itinerary.html',
        )

    return route_selection, select_itinerary


def _render_route_selection(
    request: HttpRequest,
    tracking_id: str,
    cargo_routing: CargoRouting,
    cargo_dashboard: CargoDashboard,
    template_name: str,
) -> HttpResponse:
    cargo_id = TrackingId(tracking_id)
    if request.method == 'POST':
        itinerary = _itinerary_from_token(request.POST.get('route_token'), cargo_id.value)
        if itinerary is None:
            return HttpResponseBadRequest('Invalid route selection.')
        assigned_cargo = cargo_routing.assign_route(cargo_id, itinerary)
        return redirect(f'/admin/cargo/{assigned_cargo.tracking_id.value}/')
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET', 'POST'])

    cargo = cargo_dashboard.get_cargo_details(cargo_id)
    if cargo is None:
        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
    candidates = cargo_routing.route_candidates(cargo_id)
    return render(
        request,
        template_name,
        {
            'cargo': cargo,
            'candidate_count': len(candidates),
            'route_candidates': [
                {
                    'itinerary': candidate,
                    'token': _route_selection_token(cargo_id, candidate),
                }
                for candidate in candidates
            ],
        },
    )


def _route_selection_token(tracking_id: TrackingId, itinerary: Itinerary) -> str:
    return signing.dumps(
        {
            'tracking_id': tracking_id.value,
            'legs': [
                {
                    'voyage_number': leg.voyage.voyage_number.value,
                    'load_unlocode': leg.load_location.unlocode.value,
                    'load_location': leg.load_location.name,
                    'unload_unlocode': leg.unload_location.unlocode.value,
                    'unload_location': leg.unload_location.name,
                    'load_time': leg.load_time.isoformat(),
                    'unload_time': leg.unload_time.isoformat(),
                }
                for leg in itinerary.legs
            ],
        },
        salt=_ROUTE_SELECTION_SALT,
        compress=True,
    )


def _itinerary_from_token(token: str | None, tracking_id: str) -> Itinerary | None:
    if not token:
        return None
    try:
        payload = signing.loads(token, salt=_ROUTE_SELECTION_SALT, max_age=3600)
        if payload['tracking_id'] != tracking_id:
            return None
        legs = payload['legs']
        if not isinstance(legs, list) or not legs:
            return None
        return Itinerary(
            Leg(
                Voyage(VoyageNumber(leg['voyage_number']), Schedule.EMPTY),
                Location(UnLocode(leg['load_unlocode']), leg['load_location']),
                Location(UnLocode(leg['unload_unlocode']), leg['unload_location']),
                datetime.fromisoformat(leg['load_time']),
                datetime.fromisoformat(leg['unload_time']),
            )
            for leg in legs
        )
    except (signing.BadSignature, KeyError, TypeError, ValueError):
        return None
