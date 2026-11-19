from collections.abc import Callable
from datetime import UTC, datetime

from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import redirect, render

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.cargo.domain.cargo import Cargo
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location


def _dialog_template(request: HttpRequest, name: str) -> str:
    if request.headers.get('HX-Request') == 'true':
        return f'booking/dialogs/_{name}_form.html'
    return f'booking/dialogs/{name}.html'


def _find_cargo(cargo_dashboard: CargoDashboard, tracking_id: str) -> Cargo | None:
    return cargo_dashboard.get_cargo_details(TrackingId(tracking_id))


def _not_found(request: HttpRequest, tracking_id: str) -> HttpResponse:
    template = (
        'booking/dialogs/_not_found.html'
        if request.headers.get('HX-Request') == 'true'
        else 'booking/dialogs/not_found.html'
    )
    return render(
        request,
        template,
        {'tracking_id': tracking_id},
        status=404,
    )


def _complete_dialog(request: HttpRequest) -> HttpResponse:
    if request.headers.get('HX-Request') == 'true':
        return HttpResponse(headers={'HX-Refresh': 'true'})
    return redirect('/admin/dashboard/')


def _parse_deadline(value: str) -> datetime:
    for date_format in ('%m/%d/%Y', '%m/%d/%y'):
        try:
            return datetime.strptime(value, date_format).replace(tzinfo=UTC)
        except ValueError:
            continue
    raise ValueError


def create_booking_dialog_views(
    cargo_specification: CargoSpecification,
    cargo_dashboard: CargoDashboard,
    list_shipping_locations: Callable[[], list[Location]],
) -> tuple[
    Callable[[HttpRequest, str], HttpResponse],
    Callable[[HttpRequest, str], HttpResponse],
]:
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        if request.method not in {'GET', 'POST'}:
            return HttpResponseNotAllowed(['GET', 'POST'])
        cargo = _find_cargo(cargo_dashboard, tracking_id)
        if cargo is None:
            return _not_found(request, tracking_id)

        origin = cargo.route_specification.origin
        current_destination = cargo.route_specification.destination
        locations = list_shipping_locations()
        destinations = [
            location for location in locations if location not in {origin, current_destination}
        ]
        destination_error = ''
        if request.method == 'POST':
            destination_code = request.POST.get('destination', '')
            destination = next(
                (
                    location
                    for location in destinations
                    if location.unlocode.value == destination_code
                ),
                None,
            )
            if destination is None:
                destination_error = 'Select a valid destination.'
            else:
                cargo_specification.change_destination(cargo.tracking_id, destination)
                return _complete_dialog(request)

        return render(
            request,
            _dialog_template(request, 'destination'),
            {
                'action': request.path,
                'origin': origin,
                'current_destination': current_destination,
                'destinations': destinations,
                'destination_error': destination_error,
            },
        )

    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        if request.method not in {'GET', 'POST'}:
            return HttpResponseNotAllowed(['GET', 'POST'])
        cargo = _find_cargo(cargo_dashboard, tracking_id)
        if cargo is None:
            return _not_found(request, tracking_id)

        deadline = cargo.route_specification.arrival_deadline
        deadline_value = f'{deadline.month}/{deadline.day}/{deadline.year % 100:02d}'
        deadline_error = ''
        if request.method == 'POST':
            deadline_value = request.POST.get('deadline', '')
            try:
                parsed_deadline = _parse_deadline(deadline_value)
            except ValueError:
                deadline_error = 'Enter a valid arrival deadline.'
            else:
                cargo_specification.change_deadline(cargo.tracking_id, parsed_deadline)
                return _complete_dialog(request)

        return render(
            request,
            _dialog_template(request, 'deadline'),
            {
                'action': request.path,
                'origin': cargo.route_specification.origin,
                'destination': cargo.route_specification.destination,
                'deadline_value': deadline_value,
                'deadline_error': deadline_error,
            },
        )

    return destination_dialog, deadline_dialog
