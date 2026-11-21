from collections.abc import Callable

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.routing import CargoRouting
from cargotracker.cargo.domain.tracking_id import TrackingId


def create_route_selection_views(
    cargo_routing: CargoRouting,
    cargo_dashboard: CargoDashboard | None = None,
) -> tuple[
    Callable[[HttpRequest, str], HttpResponse],
    Callable[[HttpRequest, str], HttpResponse],
    Callable[[HttpRequest, str], HttpResponse],
]:
    def _find_cargo(tracking_id: str):
        if cargo_dashboard is not None:
            cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
        else:
            cargo = cargo_routing._cargo_repository.find(TrackingId(tracking_id))
        if cargo is None:
            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
        return cargo

    def _render_route_selection(
        request: HttpRequest,
        tracking_id: str,
        template: str,
    ) -> HttpResponse:
        cargo = _find_cargo(tracking_id)
        candidates = cargo_routing.route_candidates(TrackingId(tracking_id))
        return render(
            request,
            template,
            {
                'cargo': cargo,
                'candidates': candidates,
                'candidate_count': len(candidates),
            },
        )

    def route_selection(request: HttpRequest, tracking_id: str) -> HttpResponse:
        return _render_route_selection(
            request,
            tracking_id,
            'booking/route_selection/route.html',
        )

    def itinerary_selection(request: HttpRequest, tracking_id: str) -> HttpResponse:
        return _render_route_selection(
            request,
            tracking_id,
            'booking/route_selection/itineraries.html',
        )

    def assign_route(request: HttpRequest, tracking_id: str) -> HttpResponse:
        if request.method != 'POST':
            return redirect(f'/admin/cargo/{tracking_id}/route/')
        candidates = cargo_routing.route_candidates(TrackingId(tracking_id))
        try:
            candidate_index = int(request.POST.get('candidate', ''))
        except (TypeError, ValueError):
            candidate_index = -1
        if candidate_index < 0 or candidate_index >= len(candidates):
            raise Http404('No route candidate was selected.')
        cargo_routing.assign_route(TrackingId(tracking_id), candidates[candidate_index])
        return redirect(f'/admin/cargo/{tracking_id}/')

    return route_selection, itinerary_selection, assign_route
