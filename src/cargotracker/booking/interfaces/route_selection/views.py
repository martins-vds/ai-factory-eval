from collections.abc import Callable

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.routing import CargoRouting
from cargotracker.cargo.domain.tracking_id import TrackingId


def create_route_selection_views(
    cargo_dashboard: CargoDashboard,
    cargo_routing: CargoRouting,
) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
    @require_http_methods(['GET', 'POST'])
    def select_route(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo_tracking_id = TrackingId(tracking_id)
        cargo = cargo_dashboard.get_cargo_details(cargo_tracking_id)
        if cargo is None:
            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')

        candidates = cargo_routing.route_candidates(cargo_tracking_id)
        selection_error = None
        if request.method == 'POST':
            try:
                candidate_index = int(request.POST.get('candidate_index', ''))
            except ValueError:
                candidate_index = -1

            if not 0 <= candidate_index < len(candidates):
                selection_error = 'Select a valid itinerary.'
            else:
                cargo_routing.assign_route(cargo_tracking_id, candidates[candidate_index])
                return redirect(f'/admin/cargo/{tracking_id}/')

        return render(
            request,
            'booking/route_selection/route_selection.html',
            {
                'cargo': cargo,
                'candidates': candidates,
                'candidate_count': len(candidates),
                'selection_error': selection_error,
            },
        )

    return select_route, select_route
