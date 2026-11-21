from collections.abc import Callable

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.routing import CargoRouting
from cargotracker.cargo.domain.tracking_id import TrackingId


def _selected_candidate_index(request: HttpRequest) -> int | None:
    for name in ('route_index', 'candidate_index', 'index'):
        value = request.POST.get(name)
        if value is not None:
            try:
                return int(value)
            except (TypeError, ValueError):
                return None
    return None


def create_route_selection_views(
    cargo_routing: CargoRouting,
    cargo_dashboard: CargoDashboard,
) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
    def load_selection(request: HttpRequest, tracking_id: str) -> tuple[TrackingId, object, tuple]:
        tracking = TrackingId(tracking_id)
        cargo = cargo_dashboard.get_cargo_details(tracking)
        if cargo is None:
            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
        return tracking, cargo, cargo_routing.route_candidates(tracking)

    def assign_selection(
        request: HttpRequest, tracking: TrackingId, candidates: tuple
    ) -> HttpResponse | None:
        if request.method == 'POST':
            candidate_index = _selected_candidate_index(request)
            if candidate_index is None or candidate_index < 0 or candidate_index >= len(candidates):
                raise Http404(f'Route candidate {candidate_index} not found.')
            cargo_routing.assign_route(tracking, candidates[candidate_index])
            return redirect(f'/admin/cargo/{tracking.value}/')
        return None

    def route_selection(request: HttpRequest, tracking_id: str) -> HttpResponse:
        tracking, cargo, candidates = load_selection(request, tracking_id)
        assigned = assign_selection(request, tracking, candidates)
        if assigned is not None:
            return assigned

        return render(
            request,
            'booking/route_selection/route.html',
            {
                'cargo': cargo,
                'candidates': candidates,
            },
        )

    def itinerary_selection(request: HttpRequest, tracking_id: str) -> HttpResponse:
        tracking, cargo, candidates = load_selection(request, tracking_id)
        assigned = assign_selection(request, tracking, candidates)
        if assigned is not None:
            return assigned

        return render(
            request,
            'booking/route_selection/itineraries.html',
            {
                'cargo': cargo,
                'candidates': candidates,
            },
        )

    return route_selection, itinerary_selection
