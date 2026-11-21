from collections.abc import Callable
from datetime import date, datetime, time

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location


def create_booking_dialog_views(
    cargo_dashboard: CargoDashboard,
    cargo_specification: CargoSpecification,
    list_shipping_locations: Callable[[], list[Location]],
) -> tuple[
    Callable[[HttpRequest, str], HttpResponse],
    Callable[[HttpRequest, str], HttpResponse],
]:
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo_tracking_id = TrackingId(tracking_id)
        cargo = cargo_dashboard.get_cargo_details(cargo_tracking_id)
        if cargo is None:
            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
        all_locations = list_shipping_locations()
        locations = [
            location
            for location in all_locations
            if location
            not in (cargo.route_specification.origin, cargo.route_specification.destination)
        ]
        destination_error = ''
        if request.method == 'POST':
            destination_code = request.POST.get('destination', '')
            destination = next(
                (location for location in locations if location.unlocode.value == destination_code),
                None,
            )
            if destination is None:
                destination_error = 'Select a valid destination.'
            else:
                cargo_specification.change_destination(cargo_tracking_id, destination)
                return _dialog_completed(request)
        return render(
            request,
            'booking/dialogs/destination.html',
            {'cargo': cargo, 'locations': locations, 'destination_error': destination_error},
        )

    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo_tracking_id = TrackingId(tracking_id)
        cargo = cargo_dashboard.get_cargo_details(cargo_tracking_id)
        if cargo is None:
            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
        deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
        deadline_error = ''
        if request.method == 'POST':
            deadline_value = request.POST.get('deadline', '')
            try:
                deadline = date.fromisoformat(deadline_value)
            except ValueError:
                deadline_error = 'Enter a valid arrival deadline.'
            else:
                arrival_deadline = timezone.make_aware(datetime.combine(deadline, time.min))
                cargo_specification.change_deadline(cargo_tracking_id, arrival_deadline)
                return _dialog_completed(request)
        return render(
            request,
            'booking/dialogs/deadline.html',
            {'cargo': cargo, 'deadline_value': deadline_value, 'deadline_error': deadline_error},
        )

    return destination_dialog, deadline_dialog


def _dialog_completed(request: HttpRequest) -> HttpResponse:
    if request.headers.get('HX-Request') == 'true':
        response = HttpResponse()
        response['HX-Trigger'] = 'bookingDialogCompleted'
        return response
    return redirect('/admin/dashboard/')
