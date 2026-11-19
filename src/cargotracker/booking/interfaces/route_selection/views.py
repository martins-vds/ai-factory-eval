from collections.abc import Callable
from datetime import datetime
from urllib.parse import quote

from django.core import signing
from django.core.signing import BadSignature
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotAllowed,
)
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

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

_CANDIDATE_SALT = 'booking.route-selection.candidate'


def create_route_selection_views(
    cargo_dashboard: CargoDashboard,
    cargo_routing: CargoRouting,
) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
    def route(request: HttpRequest, tracking_id: str) -> HttpResponse:
        if request.method not in {'GET', 'HEAD'}:
            return HttpResponseNotAllowed(('GET', 'HEAD'))
        return _render_candidates(request, tracking_id, select_itinerary=False)

    def select_itinerary(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = _get_cargo(tracking_id)
        if request.method == 'POST':
            itinerary = _submitted_itinerary(request, tracking_id)
            if itinerary is None:
                return HttpResponseBadRequest('Invalid route selection.')
            cargo_routing.assign_route(TrackingId(tracking_id), itinerary)
            cargo_details_path = quote(tracking_id, safe='')
            cargo_details_url = f'/admin/cargo/{cargo_details_path}/'
            if not url_has_allowed_host_and_scheme(
                cargo_details_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return HttpResponseBadRequest('Invalid cargo details redirect.')
            return redirect(cargo_details_url)
        if request.method not in {'GET', 'HEAD'}:
            return HttpResponseNotAllowed(('GET', 'HEAD', 'POST'))
        return _render_candidates(
            request,
            tracking_id,
            select_itinerary=True,
            cargo=cargo,
        )

    def _get_cargo(tracking_id: str):
        cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
        if cargo is None:
            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
        return cargo

    def _render_candidates(
        request: HttpRequest,
        tracking_id: str,
        *,
        select_itinerary: bool,
        cargo=None,
    ) -> HttpResponse:
        if cargo is None:
            cargo = _get_cargo(tracking_id)
        candidates = [
            {
                'number': number,
                'itinerary': itinerary,
                'token': signing.dumps(
                    {
                        'tracking_id': tracking_id,
                        'legs': _serialize_legs(itinerary),
                    },
                    salt=_CANDIDATE_SALT,
                ),
            }
            for number, itinerary in enumerate(
                cargo_routing.route_candidates(TrackingId(tracking_id)),
                start=1,
            )
        ]
        return render(
            request,
            'booking/route_selection/route_selection.html',
            {
                'cargo': cargo,
                'candidates': candidates,
                'candidate_count': len(candidates),
                'select_itinerary': select_itinerary,
            },
        )

    def _submitted_itinerary(request: HttpRequest, tracking_id: str) -> Itinerary | None:
        try:
            payload = signing.loads(request.POST['candidate'], salt=_CANDIDATE_SALT)
            if payload['tracking_id'] != tracking_id:
                return None
            return _deserialize_legs(payload['legs'])
        except (BadSignature, KeyError, TypeError, ValueError):
            return None

    return route, select_itinerary


def _serialize_legs(itinerary: Itinerary) -> list[dict[str, str]]:
    return [
        {
            'voyage': leg.voyage.voyage_number.value,
            'load_code': leg.load_location.unlocode.value,
            'load_name': leg.load_location.name,
            'unload_code': leg.unload_location.unlocode.value,
            'unload_name': leg.unload_location.name,
            'load_time': leg.load_time.isoformat(),
            'unload_time': leg.unload_time.isoformat(),
        }
        for leg in itinerary.legs
    ]


def _deserialize_legs(legs: list[dict[str, str]]) -> Itinerary:
    return Itinerary(
        [
            Leg(
                Voyage(VoyageNumber(leg['voyage']), Schedule.EMPTY),
                Location(UnLocode(leg['load_code']), leg['load_name']),
                Location(UnLocode(leg['unload_code']), leg['unload_name']),
                datetime.fromisoformat(leg['load_time']),
                datetime.fromisoformat(leg['unload_time']),
            )
            for leg in legs
        ]
    )
