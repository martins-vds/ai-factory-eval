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

_TOKEN_SALT = 'booking.route-selection'


def create_route_selection_views(
    cargo_routing: CargoRouting,
    cargo_dashboard: CargoDashboard,
) -> tuple[
    Callable[[HttpRequest, str], HttpResponse],
    Callable[[HttpRequest, str], HttpResponse],
]:
    def route_selection(request: HttpRequest, tracking_id: str) -> HttpResponse:
        if request.method not in {'GET', 'POST'}:
            return HttpResponseNotAllowed(['GET', 'POST'])

        cargo_tracking_id = TrackingId(tracking_id)
        cargo = cargo_dashboard.get_cargo_details(cargo_tracking_id)
        if cargo is None:
            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')

        if request.method == 'POST':
            try:
                itinerary = _itinerary_from_token(
                    request.POST.get('candidate_token', ''),
                    cargo_tracking_id,
                )
            except (signing.BadSignature, KeyError, TypeError, ValueError):
                return HttpResponseBadRequest('Invalid route selection.')
            cargo_routing.assign_route(cargo_tracking_id, itinerary)
            return redirect(f'/admin/cargo/{tracking_id}/')

        candidates = cargo_routing.route_candidates(cargo_tracking_id)
        candidate_options = [
            {'itinerary': itinerary, 'token': _itinerary_token(cargo_tracking_id, itinerary)}
            for itinerary in candidates
        ]
        return render(
            request,
            'booking/route_selection/route_selection.html',
            {
                'cargo': cargo,
                'candidates': candidates,
                'candidate_options': candidate_options,
            },
        )

    return route_selection, route_selection


def _itinerary_token(tracking_id: TrackingId, itinerary: Itinerary) -> str:
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
        },
        salt=_TOKEN_SALT,
    )


def _itinerary_from_token(token: str, tracking_id: TrackingId) -> Itinerary:
    data = signing.loads(token, salt=_TOKEN_SALT)
    if not isinstance(data, dict) or data.get('tracking_id') != tracking_id.value:
        raise signing.BadSignature('The route selection does not match this cargo.')
    return Itinerary(
        tuple(
            Leg(
                Voyage(VoyageNumber(leg['voyage_number']), Schedule.EMPTY),
                Location(UnLocode(leg['load_unlocode']), leg['load_name']),
                Location(UnLocode(leg['unload_unlocode']), leg['unload_name']),
                datetime.fromisoformat(leg['load_time']),
                datetime.fromisoformat(leg['unload_time']),
            )
            for leg in data['legs']
        )
    )
