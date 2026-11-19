from collections.abc import Callable

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location


def create_destination_dialog_view(
    specification: CargoSpecification,
    cargo_dashboard: CargoDashboard,
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

        origin = cargo.route_specification.origin
        current_destination = cargo.route_specification.destination
        destinations = [
            location
            for location in list_shipping_locations()
            if location != origin and location != current_destination
        ]
        return render(
            request,
            'booking/dialogs/destination.html',
            {
                'cargo': cargo,
                'destinations': destinations,
                'selected_destination': destinations[0] if destinations else None,
                'destination_error': '',
                'destination_value': '',
            },
        )

    return destination_dialog
