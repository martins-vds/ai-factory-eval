from collections.abc import Callable
from datetime import UTC, date, datetime, time

from django.http import Http404, HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import redirect, render

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.cargo.domain.cargo import Cargo
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location


def _find_cargo(cargo_dashboard: CargoDashboard, tracking_id: str) -> Cargo:
    try:
        cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
    except ValueError as error:
        raise Http404 from error
    if cargo is None:
        raise Http404
    return cargo


def _complete_dialog(request: HttpRequest) -> HttpResponse:
    if request.headers.get('HX-Request') == 'true':
        response = HttpResponse(status=204)
        response['HX-Redirect'] = '/admin/dashboard/'
        return response
    return redirect('/admin/dashboard/')


def create_booking_dialog_views(
    specification: CargoSpecification,
    cargo_dashboard: CargoDashboard,
    list_shipping_locations: Callable[[], list[Location]],
) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        if request.method not in {'GET', 'POST'}:
            return HttpResponseNotAllowed(['GET', 'POST'])

        cargo = _find_cargo(cargo_dashboard, tracking_id)
        route_specification = cargo.route_specification
        locations = list_shipping_locations()
        available_destinations = [
            location
            for location in locations
            if location not in (route_specification.origin, route_specification.destination)
        ]
        error = ''

        if request.method == 'POST':
            destination_code = request.POST.get('destination')
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
                specification.change_destination(cargo.tracking_id, destination)
                return _complete_dialog(request)

        return render(
            request,
            'booking/dialogs/destination.html',
            {
                'cargo': cargo,
                'locations': available_destinations,
                'destination_error': error,
                'open_dialog': request.headers.get('HX-Request') != 'true',
            },
        )

    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        if request.method not in {'GET', 'POST'}:
            return HttpResponseNotAllowed(['GET', 'POST'])

        cargo = _find_cargo(cargo_dashboard, tracking_id)
        route_specification = cargo.route_specification
        deadline_value = route_specification.arrival_deadline.date().isoformat()
        deadline_error = ''

        if request.method == 'POST':
            deadline_value = request.POST.get('deadline', '')
            try:
                deadline = datetime.combine(
                    date.fromisoformat(deadline_value),
                    time.min,
                    tzinfo=UTC,
                )
            except ValueError:
                deadline_error = 'Enter a valid arrival deadline.'
            else:
                specification.change_deadline(cargo.tracking_id, deadline)
                return _complete_dialog(request)

        return render(
            request,
            'booking/dialogs/deadline.html',
            {
                'cargo': cargo,
                'deadline_value': deadline_value,
                'deadline_error': deadline_error,
                'open_dialog': request.headers.get('HX-Request') != 'true',
            },
        )

    return destination_dialog, deadline_dialog
