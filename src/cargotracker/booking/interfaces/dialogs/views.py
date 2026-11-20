from collections.abc import Callable
from datetime import date, datetime, time

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.cargo.domain.cargo import Cargo
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location


def _find_cargo(dashboard: CargoDashboard, tracking_id: str) -> Cargo:
    cargo = dashboard.get_cargo_details(TrackingId(tracking_id))
    if cargo is None:
        raise Http404
    return cargo


def _destination_options(
    cargo: Cargo, list_shipping_locations: Callable[[], list[Location]]
) -> list[Location]:
    return [
        location
        for location in list_shipping_locations()
        if location not in (cargo.route_specification.origin, cargo.route_specification.destination)
    ]


def _dialog_completion(request: HttpRequest, dashboard: CargoDashboard) -> HttpResponse:
    if request.headers.get('HX-Request') != 'true':
        return redirect('/admin/dashboard/')
    cargos = dashboard.get_dashboard()
    response = render(
        request,
        'booking/dashboard/not_routed_table.html',
        {'not_routed_cargos': cargos.not_routed_cargos, 'hx_swap_oob': True},
    )
    response['HX-Trigger-After-Swap'] = 'cargo-dialog-close'
    return response


def create_booking_dialog_views(
    cargo_specification: CargoSpecification,
    cargo_dashboard: CargoDashboard,
    list_shipping_locations: Callable[[], list[Location]],
) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = _find_cargo(cargo_dashboard, tracking_id)
        destination_error = ''
        destination_value = ''

        if request.method == 'POST':
            destination_value = request.POST.get('destination', '')
            destination = next(
                (
                    location
                    for location in _destination_options(cargo, list_shipping_locations)
                    if location.unlocode.value == destination_value
                ),
                None,
            )
            if destination is None:
                destination_error = 'Choose an available destination.'
            else:
                cargo_specification.change_destination(cargo.tracking_id, destination)
                return _dialog_completion(request, cargo_dashboard)

        return render(
            request,
            'booking/dialogs/destination.html',
            {
                'cargo': cargo,
                'destinations': _destination_options(cargo, list_shipping_locations),
                'destination_value': destination_value,
                'destination_error': destination_error,
            },
        )

    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = _find_cargo(cargo_dashboard, tracking_id)
        deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
        deadline_error = ''

        if request.method == 'POST':
            deadline_value = request.POST.get('deadline', '')
            try:
                new_deadline = date.fromisoformat(deadline_value)
            except ValueError:
                deadline_error = 'Enter a valid arrival deadline.'
            else:
                arrival_deadline = timezone.make_aware(datetime.combine(new_deadline, time.min))
                cargo_specification.change_deadline(cargo.tracking_id, arrival_deadline)
                return _dialog_completion(request, cargo_dashboard)

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
