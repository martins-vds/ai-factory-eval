from collections.abc import Callable
from datetime import UTC, datetime, time

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.cargo.domain.cargo import Cargo
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location


def create_dialog_views(
    cargo_specification: CargoSpecification,
    get_locations: Callable[[], list[Location]],
    cargo_dashboard: CargoDashboard,
) -> tuple[
    Callable[[HttpRequest, str], HttpResponse],
    Callable[[HttpRequest, str], HttpResponse],
]:
    def find_cargo(tracking_id: str) -> Cargo:
        cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
        if cargo is None:
            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
        return cargo

    def complete_dialog(request: HttpRequest) -> HttpResponse:
        if request.headers.get('HX-Request') != 'true':
            return redirect('/admin/dashboard/')
        cargos = cargo_dashboard.get_dashboard()
        return render(
            request,
            'booking/dashboard/not_routed_table.html',
            {'not_routed_cargos': cargos.not_routed_cargos},
        )

    def render_dialog_error(request: HttpRequest, template: str, context: dict) -> HttpResponse:
        response = render(request, template, context)
        if request.headers.get('HX-Request') == 'true':
            response['HX-Retarget'] = '#edit-dialog'
            response['HX-Reswap'] = 'innerHTML'
        return response

    def destination_context(cargo: Cargo, tracking_id: str) -> dict:
        origin = cargo.route_specification.origin
        current_destination = cargo.route_specification.destination
        destinations = [
            location
            for location in get_locations()
            if location.unlocode not in {origin.unlocode, current_destination.unlocode}
        ]
        return {
            'tracking_id': tracking_id,
            'origin': origin,
            'current_destination': current_destination,
            'destinations': destinations,
            'error': '',
            'action_url': f'/admin/cargo/{tracking_id}/destination/',
        }

    @require_http_methods(['GET', 'POST'])
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = find_cargo(tracking_id)
        context = destination_context(cargo, tracking_id)
        if request.method == 'POST':
            selected_code = request.POST.get('destination', '')
            destination = next(
                (
                    location
                    for location in context['destinations']
                    if location.unlocode.value == selected_code
                ),
                None,
            )
            if destination is None:
                context['error'] = 'Select a valid destination.'
                context['selected_destination'] = selected_code
                return render_dialog_error(request, 'booking/dialogs/destination.html', context)
            cargo_specification.change_destination(TrackingId(tracking_id), destination)
            return complete_dialog(request)
        return render(request, 'booking/dialogs/destination.html', context)

    @require_http_methods(['GET', 'POST'])
    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = find_cargo(tracking_id)
        deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
        error = ''
        if request.method == 'POST':
            deadline_value = request.POST.get('deadline', '')
            try:
                deadline_date = datetime.strptime(deadline_value, '%Y-%m-%d').date()
            except ValueError:
                error = 'Enter a valid arrival deadline.'
            else:
                deadline = datetime.combine(deadline_date, time.min, tzinfo=UTC)
                cargo_specification.change_deadline(TrackingId(tracking_id), deadline)
                return complete_dialog(request)
        context = {
            'origin': cargo.route_specification.origin,
            'destination': cargo.route_specification.destination,
            'deadline_value': deadline_value,
            'error': error,
            'action_url': f'/admin/cargo/{tracking_id}/deadline/',
        }
        if error:
            return render_dialog_error(request, 'booking/dialogs/deadline.html', context)
        return render(request, 'booking/dialogs/deadline.html', context)

    return destination_dialog, deadline_dialog
