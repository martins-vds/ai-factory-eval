from collections.abc import Callable
from datetime import date, datetime, time

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.cargo.domain.cargo import Cargo
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location


def _cargo_for_dialog(cargo_dashboard: CargoDashboard, tracking_id: str) -> Cargo | None:
    try:
        return cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
    except ValueError:
        return None


def _destination_options(locations: list[Location], cargo: Cargo) -> list[Location]:
    excluded = {
        cargo.route_specification.origin.unlocode.value,
        cargo.route_specification.destination.unlocode.value,
    }
    return [location for location in locations if location.unlocode.value not in excluded]


def _completion_response(request: HttpRequest) -> HttpResponse:
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
        cargo = _cargo_for_dialog(cargo_dashboard, tracking_id)
        if cargo is None:
            return render(
                request,
                'booking/dialogs/not_found.html',
                {'tracking_id': tracking_id},
                status=404,
            )

        locations = _destination_options(list_shipping_locations(), cargo)
        selected_destination = request.POST.get('destination', '')
        destination = next(
            (
                location
                for location in locations
                if location.unlocode.value == selected_destination
            ),
            None,
        )
        destination_error = ''
        if request.method == 'POST':
            if destination is None:
                destination_error = 'Select an available destination.'
            else:
                cargo_specification.change_destination(cargo.tracking_id, destination)
                return _completion_response(request)

        return render(
            request,
            'booking/dialogs/destination.html',
            {
                'cargo': cargo,
                'locations': locations,
                'selected_destination': selected_destination,
                'destination_error': destination_error,
            },
        )

    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = _cargo_for_dialog(cargo_dashboard, tracking_id)
        if cargo is None:
            return render(
                request,
                'booking/dialogs/not_found.html',
                {'tracking_id': tracking_id},
                status=404,
            )

        deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
        deadline_error = ''
        if request.method == 'POST':
            deadline_value = request.POST.get('deadline', '')
            try:
                deadline = date.fromisoformat(deadline_value)
            except ValueError:
                deadline_error = 'Enter a valid arrival deadline.'
            else:
                arrival_deadline = timezone.make_aware(
                    datetime.combine(deadline, time.min),
                )
                cargo_specification.change_deadline(cargo.tracking_id, arrival_deadline)
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
