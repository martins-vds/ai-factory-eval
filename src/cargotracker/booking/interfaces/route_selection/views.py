from collections.abc import Callable
from datetime import datetime

from django.core import signing
from django.http import Http404, HttpRequest, HttpResponse
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

NO_ROUTE_GUIDANCE = (
    'No routes found that satisfy the route specification. '
    'Try setting an arrival deadline further into the future (a few weeks at least).'
)
_CANDIDATE_SIGNING_SALT = 'booking.route_selection'


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
        },
        salt=_CANDIDATE_SIGNING_SALT,
    )


def _selected_itinerary(token: str, tracking_id: TrackingId) -> Itinerary:
    payload = signing.loads(token, salt=_CANDIDATE_SIGNING_SALT)
    if not isinstance(payload, dict) or payload.get('tracking_id') != tracking_id.value:
        raise ValueError('The route selection does not match this cargo.')
    try:
        legs = tuple(
            Leg(
                Voyage(VoyageNumber(leg['voyage_number']), Schedule.EMPTY),
                Location(UnLocode(leg['load_unlocode']), leg['load_name']),
                Location(UnLocode(leg['unload_unlocode']), leg['unload_name']),
                datetime.fromisoformat(leg['load_time']),
                datetime.fromisoformat(leg['unload_time']),
            )
            for leg in payload['legs']
        )
        return Itinerary(legs)
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError('The route selection is invalid.') from error


def create_route_selection_views(
    cargo_routing: CargoRouting,
    cargo_dashboard: CargoDashboard,
) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
    def route_selection(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo_id = TrackingId(tracking_id)
        cargo = cargo_dashboard.get_cargo_details(cargo_id)
        if cargo is None:
            raise Http404(f'Cargo with tracking ID {cargo_id} not found.')

        if request.method == 'POST':
            try:
                itinerary = _selected_itinerary(
                    request.POST.get('candidate_token', ''),
                    cargo_id,
                )
            except (signing.BadSignature, ValueError):
                return render(
                    request,
                    'booking/route_selection/selection_error.html',
                    {'tracking_id': cargo_id},
                    status=400,
                )
            cargo_routing.assign_route(cargo_id, itinerary)
            return redirect(f'/admin/cargo/{cargo_id.value}/')

        candidates = [
            {'itinerary': itinerary, 'token': _candidate_token(cargo_id, itinerary)}
            for itinerary in cargo_routing.route_candidates(cargo_id)
        ]
        context = {
            'cargo': cargo,
            'candidates': candidates,
            'no_route_guidance': NO_ROUTE_GUIDANCE,
        }
        return render(request, 'booking/route_selection/route.html', context)

    return route_selection, route_selection
