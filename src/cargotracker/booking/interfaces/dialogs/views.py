from collections.abc import Callable
from datetime import date, datetime, time

from django.http import Http404, HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.utils import timezone

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.cargo.domain.cargo import Cargo
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location


def _cargo_for_dialog(
    cargo_dashboard: CargoDashboard, tracking_id: str
) -> tuple[TrackingId, Cargo]:
    try:
        cargo_id = TrackingId(tracking_id)
    except ValueError as error:
        raise Http404 from error
    cargo = cargo_dashboard.get_cargo_details(cargo_id)
    if cargo is None:
        raise Http404
    return cargo_id, cargo


def _render_dialog(request: HttpRequest, name: str, context: dict[str, object]) -> HttpResponse:
    template = (
        f'booking/dialogs/_{name}_form.html'
        if request.headers.get('HX-Request') == 'true'
        else f'booking/dialogs/{name}.html'
    )
    return render(request, template, context)


def _complete_dialog(request: HttpRequest) -> HttpResponse:
    if request.headers.get('HX-Request') == 'true':
        response = HttpResponse(status=204)
        response['HX-Redirect'] = '/admin/dashboard/'
        return response
    return redirect('/admin/dashboard/')


def create_booking_dialog_views(
    cargo_dashboard: CargoDashboard,
    cargo_specification: CargoSpecification,
    list_shipping_locations: Callable[[], list[Location]],
) -> tuple[
    Callable[[HttpRequest, str], HttpResponse],
    Callable[[HttpRequest, str], HttpResponse],
]:
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        if request.method not in {'GET', 'POST'}:
            return HttpResponseNotAllowed(['GET', 'POST'])
        cargo_id, cargo = _cargo_for_dialog(cargo_dashboard, tracking_id)
        route_specification = cargo.route_specification
        locations = list_shipping_locations()
        destinations = [
            location
            for location in locations
            if location != route_specification.origin
            and location != route_specification.destination
        ]
        error = ''
        if request.method == 'POST':
            destination_by_code = {location.unlocode.value: location for location in destinations}
            destination = destination_by_code.get(request.POST.get('destination'))
            if destination is None:
                error = 'Select a valid destination.'
            else:
                try:
                    cargo_specification.change_destination(cargo_id, destination)
                except LookupError as exception:
                    raise Http404 from exception
                return _complete_dialog(request)
        return _render_dialog(
            request,
            'destination',
            {
                'action': request.path,
                'cargo': cargo,
                'destinations': destinations,
                'error': error,
            },
        )

    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        if request.method not in {'GET', 'POST'}:
            return HttpResponseNotAllowed(['GET', 'POST'])
        cargo_id, cargo = _cargo_for_dialog(cargo_dashboard, tracking_id)
        error = ''
        deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
        if request.method == 'POST':
            deadline_value = request.POST.get('deadline', '')
            try:
                deadline = date.fromisoformat(deadline_value)
            except ValueError:
                error = 'Enter a valid arrival deadline.'
            else:
                arrival_deadline = timezone.make_aware(datetime.combine(deadline, time.min))
                try:
                    cargo_specification.change_deadline(cargo_id, arrival_deadline)
                except LookupError as exception:
                    raise Http404 from exception
                return _complete_dialog(request)
        return _render_dialog(
            request,
            'deadline',
            {
                'action': request.path,
                'cargo': cargo,
                'deadline_value': deadline_value,
                'error': error,
            },
        )

    return destination_dialog, deadline_dialog
