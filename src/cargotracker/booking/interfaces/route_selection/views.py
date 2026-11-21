from collections.abc import Callable
from datetime import datetime

from django.core import signing
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotAllowed,
)
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


def _candidate_token(tracking_id: TrackingId, itinerary: Itinerary) -> str:
    return signing.dumps(
        {
            'tracking_id': tracking_id.value,
            'legs': [
                {
                    'voyage_number': leg.voyage.voyage_number.value,
                    'load_unlocode': leg.load_location.unlocode.value,
                    'load_name': leg.load_location.name,
                    'unload_unlocode': leg.unload_location.unlocode.value,
                    'unload_name': leg.unload_location.name,
                    'load_time': leg.load_time.isoformat(),
                    'unload_time': leg.unload_time.isoformat(),
                }
                for leg in itinerary.legs
            ],
        }
    )


def _itinerary_from_token(token: str, tracking_id: TrackingId) -> Itinerary:
    payload = signing.loads(token)
    if payload['tracking_id'] != tracking_id.value or not payload['legs']:
        raise signing.BadSignature('Invalid itinerary selection')

    return Itinerary(
        tuple(
            Leg(
                Voyage(VoyageNumber(leg['voyage_number']), Schedule.EMPTY),
                Location(UnLocode(leg['load_unlocode']), leg['load_name']),
                Location(UnLocode(leg['unload_unlocode']), leg['unload_name']),
                datetime.fromisoformat(leg['load_time']),
                datetime.fromisoformat(leg['unload_time']),
            )
            for leg in payload['legs']
        )
    )


def create_route_selection_views(
    cargo_routing: CargoRouting,
    cargo_dashboard: CargoDashboard,
) -> tuple[
    Callable[[HttpRequest, str], HttpResponse],
    Callable[[HttpRequest, str], HttpResponse],
]:
    def route_selection(request: HttpRequest, tracking_id: str) -> HttpResponse:
        if request.method != 'GET':
            return HttpResponseNotAllowed(['GET'])
        return _render_selection(
            request,
            tracking_id,
            'booking/route_selection/route.html',
            cargo_routing,
            cargo_dashboard,
        )

    def select_itinerary(request: HttpRequest, tracking_id: str) -> HttpResponse:
        if request.method == 'POST':
            cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
            if cargo is None:
                raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
            try:
                itinerary = _itinerary_from_token(
                    request.POST.get('itinerary_token', ''),
                    cargo.tracking_id,
                )
            except (signing.BadSignature, KeyError, TypeError, ValueError):
                return HttpResponseBadRequest('Invalid itinerary selection.')
            cargo_routing.assign_route(cargo.tracking_id, itinerary)
            return redirect(f'/admin/cargo/{cargo.tracking_id.value}/')
        if request.method != 'GET':
            return HttpResponseNotAllowed(['GET', 'POST'])
        return _render_selection(
            request,
            tracking_id,
            'booking/route_selection/select_itinerary.html',
            cargo_routing,
            cargo_dashboard,
        )

    return route_selection, select_itinerary


def _render_selection(
    request: HttpRequest,
    tracking_id: str,
    template_name: str,
    cargo_routing: CargoRouting,
    cargo_dashboard: CargoDashboard,
) -> HttpResponse:
    tracking = TrackingId(tracking_id)
    cargo = cargo_dashboard.get_cargo_details(tracking)
    if cargo is None:
        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
    itineraries = cargo_routing.route_candidates(tracking)
    route_candidates = [
        {'itinerary': itinerary, 'token': _candidate_token(cargo.tracking_id, itinerary)}
        for itinerary in itineraries
    ]
    return render(
        request,
        template_name,
        {
            'cargo': cargo,
            'route_candidates': route_candidates,
        },
    )
