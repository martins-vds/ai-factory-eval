from collections.abc import Callable

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location


def create_booking_dialog_views(
    dashboard: CargoDashboard,
    specification: CargoSpecification,
    location_repository: Callable[[], list[Location]],
) -> tuple[
    Callable[[HttpRequest, str], HttpResponse],
    Callable[[HttpRequest, str], HttpResponse],
]:
    def destination(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = dashboard.get_cargo_details(TrackingId(tracking_id))
        if cargo is None:
            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')

        locations = location_repository()
        destinations = [
            location
            for location in locations
            if location not in (cargo.route_specification.origin, cargo.route_specification.destination)
        ]
        return render(
            request,
            'booking/dialogs/_destination_form.html',
            {
                'cargo': cargo,
                'destinations': destinations,
                'selected_destination': destinations[0] if destinations else None,
            },
        )

    def deadline(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = dashboard.get_cargo_details(TrackingId(tracking_id))
        if cargo is None:
            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
        return render(request, 'booking/dialogs/_deadline_form.html', {'cargo': cargo})

    return destination, deadline
