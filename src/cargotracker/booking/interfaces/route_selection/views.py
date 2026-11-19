from collections.abc import Callable
from datetime import datetime

from django.core import signing
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

_CANDIDATE_TOKEN_SALT = 'booking.route-selection.candidate'


def _candidate_token(tracking_id: TrackingId, itinerary: Itinerary) -> str:
    return signing.dumps(
        {
            'tracking_id': tracking_id.value,
            'legs': [
                {
                    'voyage': leg.voyage.voyage_number.value,
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
        salt=_CANDIDATE_TOKEN_SALT,
    )


def _itinerary_from_candidate_token(
    token: str,
    tracking_id: TrackingId,
) -> Itinerary:
    payload = signing.loads(token, salt=_CANDIDATE_TOKEN_SALT)
    if not isinstance(payload, dict) or payload.get('tracking_id') != tracking_id.value:
        raise signing.BadSignature('Candidate does not match cargo')

    try:
        legs = [
            Leg(
                Voyage(VoyageNumber(item['voyage']), Schedule.EMPTY),
                Location(
                    UnLocode(item['load_location']['unlocode']),
                    item['load_location']['name'],
                ),
                Location(
                    UnLocode(item['unload_location']['unlocode']),
                    item['unload_location']['name'],
                ),
                datetime.fromisoformat(item['load_time']),
                datetime.fromisoformat(item['unload_time']),
            )
            for item in payload['legs']
        ]
        return Itinerary(legs)
    except (KeyError, TypeError, ValueError) as error:
        raise signing.BadSignature('Invalid candidate itinerary') from error


def create_route_selection_view(
    cargo_routing: CargoRouting,
    cargo_dashboard: CargoDashboard,
) -> Callable[[HttpRequest, str], HttpResponse]:
    def route_selection(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo_tracking_id = TrackingId(tracking_id)
        cargo = cargo_dashboard.get_cargo_details(cargo_tracking_id)
        if cargo is None:
            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')

        if request.method == 'POST':
            try:
                itinerary = _itinerary_from_candidate_token(
                    request.POST['candidate_token'],
                    cargo_tracking_id,
                )
            except (KeyError, signing.BadSignature, TypeError, ValueError):
                return HttpResponseBadRequest('Invalid route selection.')

            cargo_routing.assign_route(cargo_tracking_id, itinerary)
            return redirect(f'/admin/cargo/{cargo_tracking_id.value}/')

        candidates = [
            {
                'itinerary': itinerary,
                'token': _candidate_token(cargo_tracking_id, itinerary),
            }
            for itinerary in cargo_routing.route_candidates(cargo_tracking_id)
        ]
        return render(
            request,
            'booking/route_selection/route_selection.html',
            {'cargo': cargo, 'candidates': candidates},
        )

    return route_selection
