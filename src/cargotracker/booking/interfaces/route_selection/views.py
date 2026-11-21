from collections.abc import Callable
from datetime import datetime

from django.core import signing
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse

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

_CANDIDATE_SALT = 'cargotracker.booking.route_selection'
_ROUTE_NO_CANDIDATES = (
    'No routes found that satisfy the route specification. '
    'Try setting an arrival deadline further into the future.'
)
_ITINERARY_NO_CANDIDATES = (
    'No routes found that satisfy the route specification. '
    'Try setting an arrival deadline further into the future (a few weeks at least).'
)


def create_route_selection_views(
    cargo_routing: CargoRouting,
    cargo_dashboard: CargoDashboard,
) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
    def route_selection(request: HttpRequest, tracking_id: str) -> HttpResponse:
        return _route_selection(
            request,
            tracking_id,
            'booking/route_selection/route.html',
            _ROUTE_NO_CANDIDATES,
        )

    def select_itinerary(request: HttpRequest, tracking_id: str) -> HttpResponse:
        return _route_selection(
            request,
            tracking_id,
            'booking/route_selection/select_itinerary.html',
            _ITINERARY_NO_CANDIDATES,
        )

    def _route_selection(
        request: HttpRequest,
        tracking_id: str,
        template_name: str,
        no_candidate_message: str,
    ) -> HttpResponse:
        cargo_tracking_id = TrackingId(tracking_id)
        cargo = cargo_dashboard.get_cargo_details(cargo_tracking_id)
        if cargo is None:
            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')

        if request.method == 'POST':
            itinerary = _decode_candidate(request.POST.get('candidate'), tracking_id)
            if itinerary is None:
                return HttpResponseBadRequest('Invalid route selection.')
            cargo_routing.assign_route(cargo_tracking_id, itinerary)
            return redirect(reverse('cargo_details', kwargs={'tracking_id': tracking_id}))

        candidates = cargo_routing.route_candidates(cargo_tracking_id)
        routes = [
            {
                'number': number,
                'itinerary': itinerary,
                'selection': _encode_candidate(tracking_id, itinerary),
            }
            for number, itinerary in enumerate(candidates, start=1)
        ]
        return render(
            request,
            template_name,
            {
                'cargo': cargo,
                'candidate_count': len(routes),
                'no_candidate_message': no_candidate_message,
                'routes': routes,
            },
        )

    return route_selection, select_itinerary


def _encode_candidate(tracking_id: str, itinerary: Itinerary) -> str:
    return signing.dumps(
        {
            'tracking_id': tracking_id,
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
        compress=True,
    )


def _decode_candidate(candidate: str | None, tracking_id: str) -> Itinerary | None:
    if not candidate:
        return None

    try:
        payload = signing.loads(candidate, salt=_CANDIDATE_SALT)
        if not isinstance(payload, dict) or payload.get('tracking_id') != tracking_id:
            return None
        leg_data = payload.get('legs')
        if not isinstance(leg_data, list) or not leg_data:
            return None
        legs = [
            Leg(
                Voyage(VoyageNumber(leg['voyage_number']), Schedule.EMPTY),
                _location(leg['load_location']),
                _location(leg['unload_location']),
                datetime.fromisoformat(leg['load_time']),
                datetime.fromisoformat(leg['unload_time']),
            )
            for leg in leg_data
        ]
        return Itinerary(legs)
    except (signing.BadSignature, KeyError, TypeError, ValueError):
        return None


def _location(location: dict[str, str]) -> Location:
    return Location(UnLocode(location['unlocode']), location['name'])
