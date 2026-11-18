from collections.abc import Callable
from datetime import datetime

from django.core import signing
from django.core.signing import BadSignature
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseBadRequest
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

_CANDIDATE_SALT = 'cargotracker.booking.route-selection'


def _candidate_token(tracking_id: TrackingId, itinerary: Itinerary) -> str:
    return signing.dumps(
        {
            'tracking_id': tracking_id.value,
            'legs': [
                {
                    'voyage_number': leg.voyage.voyage_number.value,
                    'load_location': {
                        'unlocode': leg.load_location.unlocode.value,
                        'name': leg.load_location.name,
                    },
                    'unload_location': {
                        'unlocode': leg.unload_location.unlocode.value,
                        'name': leg.unload_location.name,
                    },
                    'load_time': leg.load_time.isoformat(),
                    'unload_time': leg.unload_time.isoformat(),
                }
                for leg in itinerary.legs
            ],
        },
        salt=_CANDIDATE_SALT,
    )


def _itinerary_from_token(token: str, tracking_id: TrackingId) -> Itinerary:
    data = signing.loads(token, salt=_CANDIDATE_SALT)
    if data.get('tracking_id') != tracking_id.value:
        raise BadSignature('Candidate does not belong to this cargo.')

    return Itinerary(
        tuple(
            Leg(
                Voyage(VoyageNumber(leg['voyage_number']), Schedule.EMPTY),
                Location(
                    UnLocode(leg['load_location']['unlocode']),
                    leg['load_location']['name'],
                ),
                Location(
                    UnLocode(leg['unload_location']['unlocode']),
                    leg['unload_location']['name'],
                ),
                datetime.fromisoformat(leg['load_time']),
                datetime.fromisoformat(leg['unload_time']),
            )
            for leg in data['legs']
        )
    )


def create_route_selection_views(
    cargo_dashboard: CargoDashboard,
    cargo_routing: CargoRouting,
) -> tuple[
    Callable[[HttpRequest, str], HttpResponse],
    Callable[[HttpRequest, str], HttpResponse],
]:
    def show_routes(
        request: HttpRequest,
        tracking_id: str,
        template_name: str,
        empty_message: str,
    ) -> HttpResponse:
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
            except (BadSignature, KeyError, TypeError, ValueError):
                return HttpResponseBadRequest('Invalid route selection.')
            cargo_routing.assign_route(cargo_tracking_id, itinerary)
            return redirect(f'/admin/cargo/{tracking_id}/')

        candidates = cargo_routing.route_candidates(cargo_tracking_id)
        return render(
            request,
            template_name,
            {
                'cargo': cargo,
                'candidates': candidates,
                'candidate_options': [
                    {
                        'itinerary': itinerary,
                        'token': _candidate_token(cargo_tracking_id, itinerary),
                    }
                    for itinerary in candidates
                ],
                'empty_message': empty_message,
                'assignment_url': request.path,
            },
        )

    def route_selection(request: HttpRequest, tracking_id: str) -> HttpResponse:
        return show_routes(
            request,
            tracking_id,
            'booking/route_selection/route.html',
            'No routes found that satisfy the route specification. '
            'Try setting an arrival deadline further into the future.',
        )

    def select_itinerary(request: HttpRequest, tracking_id: str) -> HttpResponse:
        return show_routes(
            request,
            tracking_id,
            'booking/route_selection/select_itinerary.html',
            'No routes found that satisfy the route specification. Try setting an arrival '
            'deadline further into the future (a few weeks at least).',
        )

    return route_selection, select_itinerary
