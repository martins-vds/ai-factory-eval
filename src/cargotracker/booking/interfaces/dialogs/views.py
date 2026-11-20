from collections.abc import Callable
from datetime import date, datetime, time

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.cargo.domain.cargo import Cargo
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location


def _find_cargo(cargo_dashboard: CargoDashboard, tracking_id: str) -> Cargo | None:
    return cargo_dashboard.get_cargo_details(TrackingId(tracking_id))


def _dialog_template(request: HttpRequest, name: str) -> str:
    page_suffix = '' if request.headers.get('HX-Request') == 'true' else '_page'
    return f'booking/dialogs/{name}{page_suffix}.html'


def _not_found_response(request: HttpRequest, tracking_id: str) -> HttpResponse:
    return render(
        request,
        _dialog_template(request, 'not_found'),
        {'tracking_id': tracking_id},
        status=404,
    )


def _complete_dialog_update(request: HttpRequest) -> HttpResponse:
    if request.headers.get('HX-Request') == 'true':
        response = HttpResponse(status=204)
        response['HX-Redirect'] = '/admin/dashboard/'
        return response
    return redirect('/admin/dashboard/')


def create_dialog_views(
    cargo_dashboard: CargoDashboard,
    cargo_specification: CargoSpecification,
    list_shipping_locations: Callable[[], list[Location]],
) -> tuple[
    Callable[[HttpRequest, str], HttpResponse],
    Callable[[HttpRequest, str], HttpResponse],
]:
    @require_http_methods(['GET', 'POST'])
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = _find_cargo(cargo_dashboard, tracking_id)
        if cargo is None:
            return _not_found_response(request, tracking_id)

        route_specification = cargo.route_specification
        destinations = [
            location
            for location in list_shipping_locations()
            if location not in (route_specification.origin, route_specification.destination)
        ]
        destination_value = (
            request.POST.get('destination', '')
            if request.method == 'POST'
            else (destinations[0].unlocode.value if destinations else '')
        )
        destination_error = ''

        if request.method == 'POST':
            destination_by_code = {location.unlocode.value: location for location in destinations}
            destination = destination_by_code.get(destination_value)
            if destination is None:
                destination_error = 'Select a valid destination.'
            else:
                try:
                    cargo_specification.change_destination(TrackingId(tracking_id), destination)
                except LookupError:
                    return _not_found_response(request, tracking_id)
                return _complete_dialog_update(request)

        return render(
            request,
            _dialog_template(request, 'destination'),
            {
                'cargo': cargo,
                'destinations': destinations,
                'destination_value': destination_value,
                'destination_error': destination_error,
            },
        )

    @require_http_methods(['GET', 'POST'])
    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = _find_cargo(cargo_dashboard, tracking_id)
        if cargo is None:
            return _not_found_response(request, tracking_id)

        deadline_value = (
            request.POST.get('deadline', '')
            if request.method == 'POST'
            else cargo.route_specification.arrival_deadline.date().isoformat()
        )
        deadline_error = ''

        if request.method == 'POST':
            try:
                arrival_date = date.fromisoformat(deadline_value)
                if arrival_date.isoformat() != deadline_value:
                    raise ValueError
            except ValueError:
                deadline_error = 'Enter a valid arrival deadline.'
            else:
                arrival_deadline = timezone.make_aware(datetime.combine(arrival_date, time.min))
                try:
                    cargo_specification.change_deadline(TrackingId(tracking_id), arrival_deadline)
                except LookupError:
                    return _not_found_response(request, tracking_id)
                return _complete_dialog_update(request)

        return render(
            request,
            _dialog_template(request, 'deadline'),
            {
                'cargo': cargo,
                'deadline_value': deadline_value,
                'deadline_error': deadline_error,
            },
        )

    return destination_dialog, deadline_dialog
