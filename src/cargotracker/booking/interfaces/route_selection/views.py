from collections.abc import Callable
from datetime import datetime

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

NO_ROUTES_MESSAGE = (
    'No routes found that satisfy the route specification. Try setting an arrival deadline '
    'further into the future (a few weeks at least).'
)


def _serialize_itinerary(itinerary: Itinerary) -> list[dict[str, str]]:
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


def _deserialize_itinerary(legs: list[dict[str, str]]) -> Itinerary:
    return Itinerary(
        tuple(
            Leg(
                Voyage(VoyageNumber(leg['voyage']), Schedule.EMPTY),
                Location(UnLocode(leg['load_code']), leg['load_name']),
                Location(UnLocode(leg['unload_code']), leg['unload_name']),
                datetime.fromisoformat(leg['load_time']),
                datetime.fromisoformat(leg['unload_time']),
            )
            for leg in legs
        )
    )


def create_route_selection_views(
    cargo_routing: CargoRouting,
    cargo_dashboard: CargoDashboard,
) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
    def selection_view(
        request: HttpRequest, tracking_id: str, template_name: str, heading: str
    ) -> HttpResponse:
        cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
        if cargo is None:
            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')

        session_key = f'booking_route_candidates:{cargo.tracking_id.value}'
        candidates = ()
        selection_error = ''
        if request.method == 'POST':
            stored_candidates = request.session.get(session_key)
            try:
                candidates = tuple(
                    _deserialize_itinerary(legs) for legs in stored_candidates
                )
            except (KeyError, TypeError, ValueError):
                candidates = ()

            try:
                candidate_index = int(request.POST.get('candidate_index', ''))
            except ValueError:
                candidate_index = -1

            if 0 <= candidate_index < len(candidates):
                cargo_routing.assign_route(cargo.tracking_id, candidates[candidate_index])
                del request.session[session_key]
                return redirect(f'/admin/cargo/{cargo.tracking_id.value}/')

            selection_error = 'Select one of the available itineraries.'
            if stored_candidates is None:
                candidates = cargo_routing.route_candidates(cargo.tracking_id)
                request.session[session_key] = [
                    _serialize_itinerary(candidate) for candidate in candidates
                ]
        else:
            candidates = cargo_routing.route_candidates(cargo.tracking_id)
            request.session[session_key] = [
                _serialize_itinerary(candidate) for candidate in candidates
            ]

        return render(
            request,
            template_name,
            {
                'cargo': cargo,
                'candidates': candidates,
                'candidate_count': len(candidates),
                'selection_error': selection_error,
                'page_heading': heading.format(tracking_id=cargo.tracking_id.value),
                'no_routes_message': NO_ROUTES_MESSAGE,
            },
        )

    def route_selection(request: HttpRequest, tracking_id: str) -> HttpResponse:
        return selection_view(
            request,
            tracking_id,
            'booking/route_selection/route.html',
            'Route Cargo {tracking_id}',
        )

    def itinerary_selection(request: HttpRequest, tracking_id: str) -> HttpResponse:
        return selection_view(
            request,
            tracking_id,
            'booking/route_selection/itineraries.html',
            'Select an itinerary for cargo {tracking_id}',
        )

    return route_selection, itinerary_selection
