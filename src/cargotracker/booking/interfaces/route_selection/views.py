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
]:
    def route(request: HttpRequest, tracking_id: str) -> HttpResponse:
        tracking = TrackingId(tracking_id)
        candidates = cargo_routing.route_candidates(tracking)
        cargo = (
            cargo_dashboard.get_cargo_details(tracking)
            if cargo_dashboard is not None
            else getattr(cargo_routing, '_find_cargo', lambda _tracking: None)(tracking)
        )
        if cargo is None:
            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
        return render(
            request,
            'booking/route_selection/route.html',
            {
                'cargo': cargo,
                'candidates': candidates,
                'candidate_count': len(candidates),
            },
        )

    def itinerary(request: HttpRequest, tracking_id: str) -> HttpResponse:
        tracking = TrackingId(tracking_id)
        candidates = cargo_routing.route_candidates(tracking)

        if request.method == 'POST':
            try:
                candidate_index = int(request.POST.get('candidate', ''))
            except (TypeError, ValueError):
                raise Http404('A valid route candidate is required.')
            if candidate_index < 0 or candidate_index >= len(candidates):
                raise Http404('A valid route candidate is required.')
            cargo_routing.assign_route(tracking, candidates[candidate_index])
            return redirect(f'/admin/cargo/{tracking_id}/')

        return render(
            request,
            'booking/route_selection/select_itinerary.html',
            {
                'tracking_id': tracking_id,
                'candidates': candidates,
                'candidate_count': len(candidates),
            },
        )

    return route, itinerary


create_route_selection_view = create_route_selection_views
