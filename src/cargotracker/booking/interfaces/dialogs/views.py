from collections.abc import Callable
from datetime import UTC, date, datetime, time

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location


def _dialog_completion(request: HttpRequest) -> HttpResponse:
    if request.headers.get('HX-Request') == 'true':
        response = HttpResponse()
        response['HX-Redirect'] = '/admin/dashboard/'
        return response
    return redirect('/admin/dashboard/')


def create_booking_dialog_views(
    cargo_dashboard: CargoDashboard,
    cargo_specification: CargoSpecification,
    list_shipping_locations: Callable[[], list[Location]],
) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
        if cargo is None:
            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')

        locations = [
            location
            for location in list(list_shipping_locations())
            if location
            not in (cargo.route_specification.origin, cargo.route_specification.destination)
        ]
        error = ''
        if request.method == 'POST':
            destination_code = request.POST.get('destination', '')
            destination = next(
                (location for location in locations if location.unlocode.value == destination_code),
                None,
            )
            if destination is None:
                error = 'Select a valid destination.'
            else:
                cargo_specification.change_destination(TrackingId(tracking_id), destination)
                return _dialog_completion(request)

        return render(
            request,
            'booking/dialogs/destination.html',
            {'cargo': cargo, 'locations': locations, 'error': error},
        )

    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
        if cargo is None:
            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')

        deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
        error = ''
        if request.method == 'POST':
            deadline_value = request.POST.get('deadline', '')
            try:
                deadline = date.fromisoformat(deadline_value)
            except ValueError:
                error = 'Enter a valid arrival deadline.'
            else:
                cargo_specification.change_deadline(
                    TrackingId(tracking_id),
                    datetime.combine(deadline, time.min, tzinfo=UTC),
                )
                return _dialog_completion(request)

        return render(
            request,
            'booking/dialogs/deadline.html',
            {'cargo': cargo, 'deadline_value': deadline_value, 'error': error},
        )

    return destination_dialog, deadline_dialog
