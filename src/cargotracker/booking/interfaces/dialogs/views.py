from collections.abc import Callable
from datetime import UTC, date, datetime, time

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location


def _update_complete(request: HttpRequest) -> HttpResponse:
    if request.headers.get('HX-Request') == 'true':
        response = HttpResponse()
        response['HX-Trigger'] = 'cargo-updated'
        return response
    return redirect('/admin/dashboard/')


def create_destination_dialog_view(
    cargo_dashboard: CargoDashboard,
    cargo_specification: CargoSpecification,
    list_shipping_locations: Callable[[], list[Location]],
) -> Callable[[HttpRequest, str], HttpResponse]:
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
        if cargo is None:
            return render(
                request,
                'booking/dialogs/not_found.html',
                {'tracking_id': tracking_id},
                status=404,
            )

        locations = list_shipping_locations()
        destinations = [
            location
            for location in locations
            if location
            not in (cargo.route_specification.origin, cargo.route_specification.destination)
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
                cargo_specification.change_destination(TrackingId(tracking_id), destination)
                return _update_complete(request)

        return render(
            request,
            'booking/dialogs/destination.html',
            {
                'cargo': cargo,
                'destinations': destinations,
                'destination_error': destination_error,
            },
        )

    return destination_dialog


def create_deadline_dialog_view(
    cargo_dashboard: CargoDashboard,
    cargo_specification: CargoSpecification,
) -> Callable[[HttpRequest, str], HttpResponse]:
    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
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
                cargo_specification.change_deadline(
                    TrackingId(tracking_id),
                    datetime.combine(deadline, time.min, tzinfo=UTC),
                )
                return _update_complete(request)

        return render(
            request,
            'booking/dialogs/deadline.html',
            {
                'cargo': cargo,
                'deadline_value': deadline_value,
                'deadline_error': deadline_error,
                'today': timezone.localdate(),
            },
        )

    return deadline_dialog
