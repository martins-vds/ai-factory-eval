from collections.abc import Callable

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.routing import CargoRouting
from cargotracker.cargo.domain.tracking_id import TrackingId


def create_route_selection_views(
    cargo_routing: CargoRouting,
    cargo_dashboard: CargoDashboard,
) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
    def route_selection(request: HttpRequest, tracking_id: str) -> HttpResponse:
        return _render_route_selection(
            request,
            tracking_id,
            cargo_routing,
            cargo_dashboard,
            'booking/route_selection/route.html',
        )

    def select_itinerary(request: HttpRequest, tracking_id: str) -> HttpResponse:
        return _render_route_selection(
            request,
            tracking_id,
            cargo_routing,
            cargo_dashboard,
            'booking/route_selection/select_itinerary.html',
        )

    return route_selection, select_itinerary


def _render_route_selection(
    request: HttpRequest,
    tracking_id: str,
    cargo_routing: CargoRouting,
    cargo_dashboard: CargoDashboard,
    template_name: str,
) -> HttpResponse:
    cargo_id = TrackingId(tracking_id)
    cargo = cargo_dashboard.get_cargo_details(cargo_id)
    if cargo is None:
        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
    candidates = cargo_routing.route_candidates(cargo_id)
    return render(
        request,
        template_name,
        {
            'cargo': cargo,
            'candidate_count': len(candidates),
            'route_candidates': [{'itinerary': candidate} for candidate in candidates],
        },
    )
