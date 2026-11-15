from collections.abc import Callable
from datetime import UTC, date, datetime, time

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location


def _dialog_response(request: HttpRequest, updated: bool = False) -> HttpResponse:
    if request.headers.get('HX-Request') == 'true':
        if updated:
            response = HttpResponse(status=204)
            response['HX-Refresh'] = 'true'
            return response
        return HttpResponse('')
    return redirect('/admin/dashboard/')


def _render_dialog(
    request: HttpRequest,
    fragment_template: str,
    page_template: str,
    context: dict[str, object],
) -> HttpResponse:
    template = fragment_template if request.headers.get('HX-Request') == 'true' else page_template
    return render(request, template, context)


def create_booking_dialog_views(
    dashboard: CargoDashboard,
    specification: CargoSpecification,
    location_repository: Callable[[], list[Location]],
) -> tuple[
    Callable[[HttpRequest, str], HttpResponse],
    Callable[[HttpRequest, str], HttpResponse],
]:
    def destination(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = dashboard.get_cargo_details(TrackingId(tracking_id))
        if cargo is None:
            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')

        locations = location_repository()
        destinations = [
            location
            for location in locations
            if location
            not in (cargo.route_specification.origin, cargo.route_specification.destination)
        ]
        if request.method == 'POST':
            if request.POST.get('action') == 'cancel':
                return _dialog_response(request)
            destination_code = request.POST.get('destination', '')
            selected_destination = next(
                (
                    location
                    for location in destinations
                    if location.unlocode.value == destination_code
                ),
                None,
            )
            if selected_destination is None:
                return _render_dialog(
                    request,
                    'booking/dialogs/_destination_form.html',
                    'booking/dialogs/destination.html',
                    {
                        'cargo': cargo,
                        'destinations': destinations,
                        'selected_destination': None,
                        'destination_value': destination_code,
                        'destination_error': 'Select a valid destination.',
                    },
                )
            specification.change_destination(cargo.tracking_id, selected_destination)
            return _dialog_response(request, updated=True)

        selected_destination = destinations[0] if destinations else None
        return _render_dialog(
            request,
            'booking/dialogs/_destination_form.html',
            'booking/dialogs/destination.html',
            {
                'cargo': cargo,
                'destinations': destinations,
                'selected_destination': selected_destination,
                'destination_value': (
                    selected_destination.unlocode.value if selected_destination is not None else ''
                ),
            },
        )

    def deadline(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = dashboard.get_cargo_details(TrackingId(tracking_id))
        if cargo is None:
            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
        deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
        if request.method == 'POST':
            if request.POST.get('action') == 'cancel':
                return _dialog_response(request)
            deadline_value = request.POST.get('deadline', '')
            try:
                arrival_deadline = datetime.combine(
                    date.fromisoformat(deadline_value),
                    time.min,
                    tzinfo=UTC,
                )
            except ValueError:
                return _render_dialog(
                    request,
                    'booking/dialogs/_deadline_form.html',
                    'booking/dialogs/deadline.html',
                    {
                        'cargo': cargo,
                        'deadline_value': deadline_value,
                        'deadline_error': 'Enter a valid arrival deadline.',
                    },
                )
            specification.change_deadline(cargo.tracking_id, arrival_deadline)
            return _dialog_response(request, updated=True)
        return _render_dialog(
            request,
            'booking/dialogs/_deadline_form.html',
            'booking/dialogs/deadline.html',
            {
                'cargo': cargo,
                'deadline_value': deadline_value,
            },
        )

    return destination, deadline
