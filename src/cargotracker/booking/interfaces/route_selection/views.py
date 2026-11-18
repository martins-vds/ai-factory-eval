from collections.abc import Callable
from datetime import datetime

from django.core import signing
from django.core.signing import BadSignature
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

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


def _candidate_token(cargo, itinerary: Itinerary) -> str:
    return signing.dumps(
        {
            'tracking_id': cargo.tracking_id.value,
            'origin': cargo.route_specification.origin.unlocode.value,
            'destination': cargo.route_specification.destination.unlocode.value,
            'arrival_deadline': cargo.route_specification.arrival_deadline.isoformat(),
            'legs': [
                {
                    'voyage': leg.voyage.voyage_number.value,
                    'load_code': leg.load_location.unlocode.value,
                    'load_name': leg.load_location.name,
                    'load_time': leg.load_time.isoformat(),
                    'unload_code': leg.unload_location.unlocode.value,
                    'unload_name': leg.unload_location.name,
                    'unload_time': leg.unload_time.isoformat(),
                }
                for leg in itinerary.legs
            ],
        },
        salt=_CANDIDATE_SALT,
    )


def _selected_itinerary(token: str, cargo) -> Itinerary:
    payload = signing.loads(token, salt=_CANDIDATE_SALT)
    if not isinstance(payload, dict) or (
        payload.get('tracking_id') != cargo.tracking_id.value
        or payload.get('origin') != cargo.route_specification.origin.unlocode.value
        or payload.get('destination') != cargo.route_specification.destination.unlocode.value
        or payload.get('arrival_deadline') != cargo.route_specification.arrival_deadline.isoformat()
    ):
        raise ValueError('Candidate does not match the current cargo route.')

    return Itinerary(
        [
            Leg(
                Voyage(VoyageNumber(leg['voyage']), Schedule.EMPTY),
                Location(UnLocode(leg['load_code']), leg['load_name']),
                Location(UnLocode(leg['unload_code']), leg['unload_name']),
                datetime.fromisoformat(leg['load_time']),
                datetime.fromisoformat(leg['unload_time']),
            )
            for leg in payload['legs']
        ]
    )


def create_route_selection_views(
    cargo_dashboard: CargoDashboard,
    cargo_routing: CargoRouting,
) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
    @require_http_methods(['GET', 'POST'])
    def select_route(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo_tracking_id = TrackingId(tracking_id)
        cargo = cargo_dashboard.get_cargo_details(cargo_tracking_id)
        if cargo is None:
            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')

        selection_error = None
        if request.method == 'POST':
            try:
                itinerary = _selected_itinerary(request.POST.get('candidate_token', ''), cargo)
            except (BadSignature, KeyError, TypeError, ValueError):
                selection_error = 'Select a valid itinerary.'
            else:
                cargo_routing.assign_route(cargo_tracking_id, itinerary)
                return redirect(f'/admin/cargo/{cargo_tracking_id.value}/')

        candidates = [
            {'itinerary': itinerary, 'token': _candidate_token(cargo, itinerary)}
            for itinerary in cargo_routing.route_candidates(cargo_tracking_id)
        ]
        return render(
            request,
            'booking/route_selection/route_selection.html',
            {
                'cargo': cargo,
                'candidates': candidates,
                'candidate_count': len(candidates),
                'selection_error': selection_error,
            },
        )

    return select_route, select_route
