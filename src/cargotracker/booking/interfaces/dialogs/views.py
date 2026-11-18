from collections.abc import Callable
from datetime import UTC, date, datetime, time

from django.http import Http404, HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import redirect, render

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.cargo.domain.cargo import Cargo
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location


def create_booking_dialog_views(
    cargo_dashboard: CargoDashboard,
    cargo_specification: CargoSpecification,
    list_shipping_locations: Callable[[], list[Location]],
) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        if request.method not in {'GET', 'POST'}:
            return HttpResponseNotAllowed(['GET', 'POST'])
        cargo = _get_cargo(cargo_dashboard, tracking_id)
        destinations = _available_destinations(
            list(list_shipping_locations()),
            cargo.route_specification.origin,
            cargo.route_specification.destination,
        )
        selected_destination = request.POST.get('destination', '')
        error = ''

        if request.method == 'POST':
            destination = next(
                (
                    location
                    for location in destinations
                    if location.unlocode.value == selected_destination
                ),
                None,
            )
            if destination is None:
                error = 'Select a valid destination.'
            else:
                cargo_specification.change_destination(TrackingId(tracking_id), destination)
                return _dialog_completed(request)

        return _render_dialog(
            request,
            'destination',
            {
                'action_url': f'/admin/cargo/{tracking_id}/destination/',
                'cargo': cargo,
                'destinations': destinations,
                'selected_destination': selected_destination,
                'error': error,
            },
        )

    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        if request.method not in {'GET', 'POST'}:
            return HttpResponseNotAllowed(['GET', 'POST'])
        cargo = _get_cargo(cargo_dashboard, tracking_id)
        deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
        error = ''

        if request.method == 'POST':
            deadline_value = request.POST.get('deadline', '')
            try:
                deadline = date.fromisoformat(deadline_value)
            except (TypeError, ValueError):
                error = 'Enter a valid arrival deadline.'
            else:
                cargo_specification.change_deadline(
                    TrackingId(tracking_id),
                    datetime.combine(deadline, time.min, tzinfo=UTC),
                )
                return _dialog_completed(request)

        return _render_dialog(
            request,
            'deadline',
            {
                'action_url': f'/admin/cargo/{tracking_id}/deadline/',
                'cargo': cargo,
                'deadline_value': deadline_value,
                'error': error,
            },
        )

    return destination_dialog, deadline_dialog


def _get_cargo(cargo_dashboard: CargoDashboard, tracking_id: str) -> Cargo:
    cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
    if cargo is None:
        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
    return cargo


def _available_destinations(
    locations: list[Location], origin: Location, current_destination: Location
) -> list[Location]:
    excluded_codes = {origin.unlocode.value, current_destination.unlocode.value}
    return [location for location in locations if location.unlocode.value not in excluded_codes]


def _render_dialog(
    request: HttpRequest, dialog_type: str, context: dict[str, object]
) -> HttpResponse:
    context['dialog_type'] = dialog_type
    template = (
        'booking/dialogs/dialog.html'
        if request.headers.get('HX-Request') == 'true'
        else f'booking/dialogs/{dialog_type}.html'
    )
    return render(request, template, context)


def _dialog_completed(request: HttpRequest) -> HttpResponse:
    if request.headers.get('HX-Request') == 'true':
        response = HttpResponse(status=204)
        response['HX-Redirect'] = '/admin/dashboard/'
        return response
    return redirect('/admin/dashboard/')
