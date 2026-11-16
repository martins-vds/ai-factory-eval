from collections.abc import Callable
from datetime import date, datetime, time

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location


def _dialog_completion() -> HttpResponse:
    response = HttpResponse(status=204)
    response['HX-Trigger'] = 'bookingDialogClose, bookingCargoUpdated'
    return response


def _cargo_context(cargo_dashboard: CargoDashboard, tracking_id: str):
    cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
    if cargo is None:
        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
    return cargo


def create_booking_dialog_views(
    cargo_specification: CargoSpecification,
    cargo_dashboard: CargoDashboard,
    list_shipping_locations: Callable[[], list[Location]],
) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
    @require_http_methods(['GET', 'POST'])
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = _cargo_context(cargo_dashboard, tracking_id)
        locations = list_shipping_locations()
        destinations = [
            location
            for location in locations
            if location
            not in (
                cargo.route_specification.origin,
                cargo.route_specification.destination,
            )
        ]
        error = ''

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
                error = 'Select a valid destination.'
            else:
                cargo_specification.change_destination(cargo.tracking_id, destination)
                return _dialog_completion()

        return render(
            request,
            'booking/dialogs/destination_form.html',
            {
                'cargo': cargo,
                'destinations': destinations,
                'error': error,
            },
        )

    @require_http_methods(['GET', 'POST'])
    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = _cargo_context(cargo_dashboard, tracking_id)
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
                    cargo.tracking_id,
                    timezone.make_aware(datetime.combine(deadline, time.min)),
                )
                return _dialog_completion()

        return render(
            request,
            'booking/dialogs/deadline_form.html',
            {
                'cargo': cargo,
                'deadline_value': deadline_value,
                'error': error,
            },
        )

    return destination_dialog, deadline_dialog
