from collections.abc import Callable
from datetime import datetime
from urllib.parse import quote

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

_CANDIDATE_SIGNING_SALT = 'cargotracker.booking.route_selection'


def _candidate_token(tracking_id: str, itinerary: Itinerary) -> str:
    return signing.dumps(
        {
            'tracking_id': tracking_id,
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


def _itinerary_from_token(
    token: str,
    tracking_id: str,
) -> Itinerary:
    payload = signing.loads(token, salt=_CANDIDATE_SIGNING_SALT)
    if not isinstance(payload, dict) or payload.get('tracking_id') != tracking_id:
        raise signing.BadSignature('Candidate does not belong to this cargo')

    legs = payload.get('legs')
    if not isinstance(legs, list) or not legs:
        raise signing.BadSignature('Candidate has no itinerary legs')

    itinerary_legs = []
    for data in legs:
        if not isinstance(data, dict):
            raise signing.BadSignature('Candidate contains an invalid itinerary leg')
        try:
            voyage = Voyage(VoyageNumber(data['voyage_number']), Schedule.EMPTY)
            load_location = Location(UnLocode(data['load_unlocode']), data['load_name'])
            unload_location = Location(UnLocode(data['unload_unlocode']), data['unload_name'])
            load_time = datetime.fromisoformat(data['load_time'])
            unload_time = datetime.fromisoformat(data['unload_time'])
        except (KeyError, TypeError, ValueError) as error:
            raise signing.BadSignature('Candidate contains an invalid itinerary leg') from error

        itinerary_legs.append(Leg(voyage, load_location, unload_location, load_time, unload_time))

    return Itinerary(itinerary_legs)


def create_route_selection_views(
    cargo_routing: CargoRouting,
    cargo_dashboard: CargoDashboard,
) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
    def route_selection(request: HttpRequest, tracking_id: str) -> HttpResponse:
        return _route_selection_response(
            request,
            tracking_id,
            'booking/route_selection/route.html',
            cargo_routing,
            cargo_dashboard,
        )

    def select_itinerary(request: HttpRequest, tracking_id: str) -> HttpResponse:
        return _route_selection_response(
            request,
            tracking_id,
            'booking/route_selection/select_itinerary.html',
            cargo_routing,
            cargo_dashboard,
        )

    return route_selection, select_itinerary


def _route_selection_response(
    request: HttpRequest,
    tracking_id: str,
    template_name: str,
    cargo_routing: CargoRouting,
    cargo_dashboard: CargoDashboard,
) -> HttpResponse:
    if request.method not in {'GET', 'POST'}:
        return HttpResponseNotAllowed(['GET', 'POST'])

    cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
    if cargo is None:
        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')

    if request.method == 'POST':
        try:
            itinerary = _itinerary_from_token(
                request.POST.get('candidate_token', ''),
                tracking_id,
            )
        except signing.BadSignature:
            return HttpResponseBadRequest('Invalid route selection.')
        cargo_routing.assign_route(TrackingId(tracking_id), itinerary)
        return redirect(f'/admin/cargo/{quote(tracking_id, safe="")}/')

    candidates = [
        {'itinerary': itinerary, 'token': _candidate_token(tracking_id, itinerary)}
        for itinerary in cargo_routing.route_candidates(TrackingId(tracking_id))
    ]
    return render(
        request,
        template_name,
        {
            'cargo': cargo,
            'candidates': candidates,
            'candidate_count': len(candidates),
            'form_action': request.path,
        },
    )
