from collections.abc import Callable

from django.http import Http404, HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.routing import CargoRouting
from cargotracker.cargo.domain.tracking_id import TrackingId


def create_route_selection_views(
    cargo_dashboard: CargoDashboard,
    cargo_routing: CargoRouting,
) -> tuple[
    Callable[[HttpRequest, str], HttpResponse],
    Callable[[HttpRequest, str], HttpResponse],
]:
    def show_routes(
        request: HttpRequest,
        tracking_id: str,
        template_name: str,
        empty_message: str,
    ) -> HttpResponse:
        cargo_tracking_id = TrackingId(tracking_id)
        cargo = cargo_dashboard.get_cargo_details(cargo_tracking_id)
        if cargo is None:
            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')

        candidates = cargo_routing.route_candidates(cargo_tracking_id)
        if request.method == 'POST':
            try:
                route_index = int(request.POST.get('route_index', ''))
            except ValueError:
                return HttpResponseBadRequest('Invalid route selection.')
            if not 0 <= route_index < len(candidates):
                return HttpResponseBadRequest('Invalid route selection.')
            cargo_routing.assign_route(cargo_tracking_id, candidates[route_index])
            return redirect(f'/admin/cargo/{tracking_id}/')

        return render(
            request,
            template_name,
            {
                'cargo': cargo,
                'candidates': candidates,
                'empty_message': empty_message,
                'assignment_url': request.path,
            },
        )

    def route_selection(request: HttpRequest, tracking_id: str) -> HttpResponse:
        return show_routes(
            request,
            tracking_id,
            'booking/route_selection/route.html',
            'No routes found that satisfy the route specification. '
            'Try setting an arrival deadline further into the future.',
        )

    def select_itinerary(request: HttpRequest, tracking_id: str) -> HttpResponse:
        return show_routes(
            request,
            tracking_id,
            'booking/route_selection/select_itinerary.html',
            'No routes found that satisfy the route specification. Try setting an arrival '
            'deadline further into the future (a few weeks at least).',
        )

    return route_selection, select_itinerary
