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


def _find_cargo(dashboard: CargoDashboard, tracking_id: str) -> Cargo:
    try:
        cargo = dashboard.get_cargo_details(TrackingId(tracking_id))
    except (TypeError, ValueError) as error:
        raise Http404(f'Cargo with tracking ID {tracking_id} not found.') from error
    if cargo is None:
        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
    return cargo


def _completion_response(request: HttpRequest) -> HttpResponse:
    if request.headers.get('HX-Request') == 'true':
        return HttpResponse(headers={'HX-Redirect': '/admin/dashboard/'})
    return redirect('/admin/dashboard/')


def create_booking_dialog_views(
    specification: CargoSpecification,
    dashboard: CargoDashboard,
    list_shipping_locations: Callable[[], list[Location]],
) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        if request.method not in {'GET', 'POST'}:
            return HttpResponseNotAllowed(('GET', 'POST'))
        cargo = _find_cargo(dashboard, tracking_id)
        locations = list_shipping_locations()
        destinations = [
            location
            for location in locations
            if location != cargo.route_specification.origin
            and location != cargo.route_specification.destination
        ]
        destination_error = ''

        if request.method == 'POST':
            destination = next(
                (
                    location
                    for location in destinations
                    if location.unlocode.value == request.POST.get('destination')
                ),
                None,
            )
            if destination is None:
                destination_error = 'Select a valid destination.'
            else:
                try:
                    specification.change_destination(TrackingId(tracking_id), destination)
                except LookupError as error:
                    raise Http404(f'Cargo with tracking ID {tracking_id} not found.') from error
                return _completion_response(request)

        return render(
            request,
            'booking/dialogs/destination.html',
            {
                'cargo': cargo,
                'destinations': destinations,
                'destination_error': destination_error,
            },
        )

    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        if request.method not in {'GET', 'POST'}:
            return HttpResponseNotAllowed(('GET', 'POST'))
        cargo = _find_cargo(dashboard, tracking_id)
        deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
        deadline_error = ''

        if request.method == 'POST':
            deadline_value = request.POST.get('deadline', '')
            try:
                deadline = date.fromisoformat(deadline_value)
            except ValueError:
                deadline = None
                deadline_error = 'Enter a valid arrival deadline.'
            if deadline is not None:
                arrival_deadline = timezone.make_aware(datetime.combine(deadline, time.min))
                try:
                    specification.change_deadline(TrackingId(tracking_id), arrival_deadline)
                except LookupError as error:
                    raise Http404(f'Cargo with tracking ID {tracking_id} not found.') from error
                return _completion_response(request)

        return render(
            request,
            'booking/dialogs/deadline.html',
            {
                'cargo': cargo,
                'deadline_value': deadline_value,
                'deadline_error': deadline_error,
            },
        )

    return destination_dialog, deadline_dialog
