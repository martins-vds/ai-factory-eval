from collections.abc import Callable
from datetime import UTC, datetime, time

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location


def _cargo_for_dialog(cargo_dashboard: CargoDashboard, tracking_id: str):
    cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
    if cargo is None:
        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
    return cargo


def _complete_dialog(request: HttpRequest) -> HttpResponse:
    if request.headers.get('HX-Request') == 'true':
        return HttpResponse(headers={'HX-Trigger': 'cargoUpdated'})
    return redirect('/admin/dashboard/')


def create_destination_dialog_view(
    specification: CargoSpecification,
    cargo_dashboard: CargoDashboard,
    list_shipping_locations: Callable[[], list[Location]],
) -> Callable[[HttpRequest, str], HttpResponse]:
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = _cargo_for_dialog(cargo_dashboard, tracking_id)
        locations = list_shipping_locations()
        available_destinations = [
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
                    for location in available_destinations
                    if location.unlocode.value == destination_code
                ),
                None,
            )
            if destination is None:
                destination_error = 'Select a valid destination.'
            else:
                specification.change_destination(cargo.tracking_id, destination)
                return _complete_dialog(request)

        return render(
            request,
            'booking/dialogs/destination.html',
            {
                'cargo': cargo,
                'available_destinations': available_destinations,
                'destination_error': destination_error,
            },
        )

    return destination_dialog


def create_deadline_dialog_view(
    specification: CargoSpecification,
    cargo_dashboard: CargoDashboard,
) -> Callable[[HttpRequest, str], HttpResponse]:
    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = _cargo_for_dialog(cargo_dashboard, tracking_id)
        deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
        deadline_error = ''

        if request.method == 'POST':
            deadline_value = request.POST.get('deadline', '')
            try:
                deadline = datetime.strptime(deadline_value, '%Y-%m-%d').date()
            except ValueError:
                deadline_error = 'Enter a valid arrival deadline.'
            else:
                specification.change_deadline(
                    cargo.tracking_id,
                    datetime.combine(deadline, time.min, tzinfo=UTC),
                )
                return _complete_dialog(request)

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
