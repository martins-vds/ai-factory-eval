from collections.abc import Callable
from datetime import UTC, date, datetime, time

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.cargo.domain.cargo import Cargo
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location


def _cargo_for_dialog(cargo_dashboard: CargoDashboard, tracking_id: str) -> Cargo | None:
    return cargo_dashboard.get_cargo_details(TrackingId(tracking_id))


def _not_found_response(request: HttpRequest, tracking_id: str) -> HttpResponse:
    return render(
        request,
        'booking/dialogs/not_found.html',
        {'tracking_id': tracking_id},
        status=404,
    )


def _dialog_success(request: HttpRequest) -> HttpResponse:
    if request.headers.get('HX-Request') == 'true':
        response = HttpResponse()
        response['HX-Redirect'] = '/admin/dashboard/'
        return response
    return redirect('/admin/dashboard/')


def create_destination_dialog_view(
    cargo_dashboard: CargoDashboard,
    cargo_specification: CargoSpecification,
    list_shipping_locations: Callable[[], list[Location]],
) -> Callable[[HttpRequest, str], HttpResponse]:
    @require_http_methods(['GET', 'POST'])
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = _cargo_for_dialog(cargo_dashboard, tracking_id)
        if cargo is None:
            return _not_found_response(request, tracking_id)
        cargo_tracking_id = TrackingId(tracking_id)
        locations = list_shipping_locations()
        available_destinations = [
            location
            for location in locations
            if location != cargo.route_specification.origin
            and location != cargo.route_specification.destination
        ]
        error = ''

        if request.method == 'POST':
            destination_code = request.POST.get('destination', '')
            destination = next(
                (
                    location
                    for location in available_destinations
                    if location.unlocode.value == destination_code
                ),
                None,
            )
            if destination is None:
                error = 'Select a valid destination.'
            else:
                cargo_specification.change_destination(cargo_tracking_id, destination)
                return _dialog_success(request)

        return render(
            request,
            'booking/dialogs/destination.html',
            {
                'cargo': cargo,
                'available_destinations': available_destinations,
                'error': error,
            },
        )

    return destination_dialog


def create_deadline_dialog_view(
    cargo_dashboard: CargoDashboard,
    cargo_specification: CargoSpecification,
) -> Callable[[HttpRequest, str], HttpResponse]:
    @require_http_methods(['GET', 'POST'])
    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = _cargo_for_dialog(cargo_dashboard, tracking_id)
        if cargo is None:
            return _not_found_response(request, tracking_id)
        deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
        error = ''

        if request.method == 'POST':
            deadline_value = request.POST.get('deadline', '')
            try:
                arrival_deadline = date.fromisoformat(deadline_value)
            except ValueError:
                error = 'Enter a valid arrival deadline.'
            else:
                cargo_specification.change_deadline(
                    TrackingId(tracking_id),
                    datetime.combine(arrival_deadline, time.min, tzinfo=UTC),
                )
                return _dialog_success(request)

        return render(
            request,
            'booking/dialogs/deadline.html',
            {'cargo': cargo, 'deadline_value': deadline_value, 'error': error},
        )

    return deadline_dialog
