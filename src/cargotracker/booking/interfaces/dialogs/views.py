from collections.abc import Callable

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location


def create_destination_dialog_view(
    cargo_dashboard: CargoDashboard,
    list_shipping_locations: Callable[[], list[Location]],
) -> Callable[[HttpRequest, str], HttpResponse]:
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
        if cargo is None:
            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
        locations = list_shipping_locations()
        destination_options = [
            location
            for location in locations
            if location not in (
                cargo.route_specification.origin,
                cargo.route_specification.destination,
            )
        ]
        return render(
            request,
            'booking/dialogs/destination.html',
            {'cargo': cargo, 'destination_options': destination_options},
        )

    return destination_dialog
