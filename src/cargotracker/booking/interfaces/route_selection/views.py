from collections.abc import Callable

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from cargotracker.booking.application.routing import CargoRouting
from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.cargo.domain.tracking_id import TrackingId


def create_route_selection_views(
    cargo_routing: CargoRouting,
    cargo_dashboard: CargoDashboard,
) -> tuple[
    Callable[..., HttpResponse],
    Callable[..., HttpResponse],
    Callable[..., HttpResponse],
]:
    def route_selection(
        request: HttpRequest,
        tracking_id: str,
        candidate_index: int | str | None = None,
    ) -> HttpResponse:
        cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
        if cargo is None:
            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')

        if request.method == 'POST':
            selected_index = candidate_index
            if selected_index is None:
                selected_index = (
                    request.POST.get('candidate_index')
                    or request.POST.get('routeIndex')
                    or request.POST.get('itineraryIndex')
                )
            return assign_candidate(request, tracking_id, selected_index)

        candidates = cargo_routing.route_candidates(TrackingId(tracking_id))
        return render(
            request,
            'booking/route_selection/route.html',
            {
                'cargo': cargo,
                'candidate_count': len(candidates),
                'candidates': candidates,
            },
        )

    def itinerary_selection(
        request: HttpRequest,
        tracking_id: str,
    ) -> HttpResponse:
        cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
        if cargo is None:
            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
        candidates = cargo_routing.route_candidates(TrackingId(tracking_id))
        return render(
            request,
            'booking/route_selection/itinerary_selection.html',
            {
                'cargo': cargo,
                'candidate_count': len(candidates),
                'candidates': candidates,
            },
        )

    def assign_candidate(
        request: HttpRequest,
        tracking_id: str,
        candidate_index: int | str | None = None,
    ) -> HttpResponse:
        if candidate_index is None:
            candidate_index = (
                request.POST.get('candidate_index')
                or request.POST.get('routeIndex')
                or request.POST.get('itineraryIndex')
            )
        if candidate_index is None:
            raise Http404('A route candidate index is required.')
        try:
            index = int(candidate_index)
        except (TypeError, ValueError) as error:
            raise Http404('A valid route candidate index is required.') from error

        candidates = cargo_routing.route_candidates(TrackingId(tracking_id))
        if index < 0 or index >= len(candidates):
            raise Http404('The route candidate was not found.')
        cargo_routing.assign_route(TrackingId(tracking_id), candidates[index])
        return redirect(f'/admin/cargo/{tracking_id}/')

    return route_selection, itinerary_selection, assign_candidate
