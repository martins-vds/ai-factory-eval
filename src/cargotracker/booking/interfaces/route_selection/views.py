from collections.abc import Callable
from typing import Any

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
    if cargo_dashboard is None:
        repository = getattr(cargo_routing, '_cargo_repository', None)
        if repository is None:
            raise TypeError('cargo_dashboard is required')
        cargo_dashboard = CargoDashboard(repository)

    def _load_cargo(tracking_id: str) -> tuple[Any, tuple[Any, ...]]:
        cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
        if cargo is None:
            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
        candidates = cargo_routing.route_candidates(TrackingId(tracking_id))
        return cargo, candidates

    def _render_route(
        request: HttpRequest,
        tracking_id: str,
        candidates: tuple[Any, ...],
        cargo: Any,
    ) -> HttpResponse:
        return render(
            request,
            'booking/route_selection/route.html',
            {
                'cargo': cargo,
                'candidates': candidates,
            },
        )

    def route(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo, candidates = _load_cargo(tracking_id)
        if request.method == 'POST':
            candidate_value = request.POST.get('candidate', request.POST.get('candidate_index'))
            try:
                candidate_index = int(candidate_value) if candidate_value is not None else -1
            except (TypeError, ValueError):
                candidate_index = -1
            if candidate_index < 0 or candidate_index >= len(candidates):
                raise Http404('The selected itinerary is not available.')
            cargo_routing.assign_route(
                TrackingId(tracking_id),
                candidates[candidate_index],
            )
            return redirect(f'/admin/cargo/{tracking_id}/')
        return _render_route(request, tracking_id, candidates, cargo)

    def itineraries(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo, candidates = _load_cargo(tracking_id)
        if request.method == 'POST':
            candidate_value = request.POST.get('candidate', request.POST.get('candidate_index'))
            try:
                candidate_index = int(candidate_value) if candidate_value is not None else -1
            except (TypeError, ValueError):
                candidate_index = -1
            if candidate_index < 0 or candidate_index >= len(candidates):
                raise Http404('The selected itinerary is not available.')
            cargo_routing.assign_route(
                TrackingId(tracking_id),
                candidates[candidate_index],
            )
            return redirect(f'/admin/cargo/{tracking_id}/')
        return _render_route(request, tracking_id, candidates, cargo)

    return route, itineraries
