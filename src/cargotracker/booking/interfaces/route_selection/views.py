from collections.abc import Callable
from datetime import datetime

from django.core import signing
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseNotAllowed
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

_CANDIDATE_SALT = 'booking.route-selection'
_CANDIDATE_MAX_AGE = 15 * 60


def _candidate_token(tracking_id: str, itinerary: Itinerary) -> str:
    return signing.dumps(
        {
            'tracking_id': tracking_id,
            'legs': [
                {
                    'voyage': leg.voyage.voyage_number.value,
                    'load': {
                        'unlocode': leg.load_location.unlocode.value,
                        'name': leg.load_location.name,
                    },
                    'unload': {
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


def _itinerary_from_token(token: str, tracking_id: str) -> Itinerary:
    payload = signing.loads(token, salt=_CANDIDATE_SALT, max_age=_CANDIDATE_MAX_AGE)
    if not isinstance(payload, dict) or payload.get('tracking_id') != tracking_id:
        raise signing.BadSignature

    legs = payload.get('legs')
    if not isinstance(legs, list) or not legs:
        raise signing.BadSignature

    return Itinerary(
        Leg(
            Voyage(VoyageNumber(leg['voyage']), Schedule.EMPTY),
            Location(UnLocode(leg['load']['unlocode']), leg['load']['name']),
            Location(UnLocode(leg['unload']['unlocode']), leg['unload']['name']),
            datetime.fromisoformat(leg['load_time']),
            datetime.fromisoformat(leg['unload_time']),
        )
        for leg in legs
    )


def create_route_selection_views(
    routing: CargoRouting, cargo_dashboard: CargoDashboard
) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
    def page(request: HttpRequest, tracking_id: str, select_itinerary: bool) -> HttpResponse:
        if request.method not in {'GET', 'POST'}:
            return HttpResponseNotAllowed(['GET', 'POST'])

        cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
        if cargo is None:
            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')

        candidate_error = ''
        response_status = 200
        if request.method == 'POST':
            try:
                itinerary = _itinerary_from_token(request.POST.get('candidate', ''), tracking_id)
            except (signing.BadSignature, KeyError, TypeError, ValueError):
                candidate_error = 'Choose a valid route.'
                response_status = 400
            else:
                if not cargo.route_specification.is_satisfied_by(itinerary):
                    candidate_error = (
                        'Choose a route that satisfies the current route specification.'
                    )
                    response_status = 400
                else:
                    routing.assign_route(TrackingId(tracking_id), itinerary)
                    return redirect(f'/admin/cargo/{tracking_id}/')

        routes = [
            {
                'number': number,
                'itinerary': itinerary,
                'token': _candidate_token(tracking_id, itinerary),
            }
            for number, itinerary in enumerate(routing.route_candidates(TrackingId(tracking_id)), 1)
        ]
        empty_message = (
            'No routes found that satisfy the route specification. '
            'Try setting an arrival deadline further into the future (a few weeks at least).'
            if select_itinerary
            else 'No routes found that satisfy the route specification. '
            'Try setting an arrival deadline further into the future.'
        )
        return render(
            request,
            'booking/route_selection/select_itinerary.html'
            if select_itinerary
            else 'booking/route_selection/route.html',
            {
                'cargo': cargo,
                'candidate_count': len(routes),
                'candidate_error': candidate_error,
                'empty_message': empty_message,
                'routes': routes,
                'select_itinerary': select_itinerary,
            },
            status=response_status,
        )

    def route(request: HttpRequest, tracking_id: str) -> HttpResponse:
        return page(request, tracking_id, False)

    def select_itinerary(request: HttpRequest, tracking_id: str) -> HttpResponse:
        return page(request, tracking_id, True)

    return route, select_itinerary
