from collections.abc import Callable
from datetime import UTC, date, datetime, time

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location


def _not_found(request: HttpRequest, tracking_id: str) -> HttpResponse:
    return render(
        request,
        'booking/dialogs/not_found.html',
        {'tracking_id': tracking_id},
        status=404,
    )


def create_destination_dialog_view(
    specification: CargoSpecification,
    cargo_dashboard: CargoDashboard,
    list_shipping_locations: Callable[[], list[Location]],
) -> Callable[[HttpRequest, str], HttpResponse]:
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
        if cargo is None:
            return _not_found(request, tracking_id)

        origin = cargo.route_specification.origin
        current_destination = cargo.route_specification.destination
        destinations = [
            location
            for location in list_shipping_locations()
            if location != origin and location != current_destination
        ]
        destination_value = request.POST.get('destination', '')
        selected_destination = next(
            (location for location in destinations if location.unlocode.value == destination_value),
            None,
        )
        destination_error = ''
        if request.method == 'POST':
            if selected_destination is None:
                destination_error = 'Select a valid destination.'
            else:
                try:
                    specification.change_destination(
                        TrackingId(tracking_id),
                        selected_destination,
                    )
                except LookupError:
                    return _not_found(request, tracking_id)
                response = HttpResponse()
                response['HX-Redirect'] = '/admin/dashboard/'
                return response
        elif selected_destination is None and destinations:
            selected_destination = destinations[0]

        return render(
            request,
            'booking/dialogs/destination.html',
            {
                'cargo': cargo,
                'destinations': destinations,
                'selected_destination': selected_destination,
                'destination_error': destination_error,
                'destination_value': destination_value,
            },
        )

    return destination_dialog


def create_deadline_dialog_view(
    specification: CargoSpecification,
    cargo_dashboard: CargoDashboard,
) -> Callable[[HttpRequest, str], HttpResponse]:
    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
        if cargo is None:
            return _not_found(request, tracking_id)

        deadline_value = request.POST.get(
            'arrival_deadline',
            cargo.route_specification.arrival_deadline.date().isoformat(),
        )
        deadline_error = ''
        if request.method == 'POST':
            try:
                arrival_date = date.fromisoformat(deadline_value)
            except ValueError:
                deadline_error = 'Enter a valid arrival deadline.'
            else:
                try:
                    specification.change_deadline(
                        TrackingId(tracking_id),
                        datetime.combine(arrival_date, time.min, tzinfo=UTC),
                    )
                except LookupError:
                    return _not_found(request, tracking_id)
                response = HttpResponse()
                response['HX-Redirect'] = '/admin/dashboard/'
                return response

        return render(
            request,
            'booking/dialogs/deadline.html',
            {
                'cargo': cargo,
                'deadline_value': deadline_value,
                'deadline_error': deadline_error,
            },
        )

    return deadline_dialog
