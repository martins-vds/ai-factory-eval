from collections.abc import Callable
from datetime import UTC, date, datetime, time

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.cargo.domain.cargo import Cargo
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location


def _find_cargo(dashboard: CargoDashboard, tracking_id: str) -> tuple[TrackingId, Cargo]:
    try:
        cargo_id = TrackingId(tracking_id)
    except ValueError as error:
        raise Http404 from error
    cargo = dashboard.get_cargo_details(cargo_id)
    if cargo is None:
        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
    return cargo_id, cargo


def _destination_dialog(
    request: HttpRequest,
    cargo: Cargo,
    locations: list[Location],
    value: str = '',
    error: str = '',
) -> HttpResponse:
    available_destinations = [
        location
        for location in locations
        if location not in (cargo.route_specification.origin, cargo.route_specification.destination)
    ]
    return render(
        request,
        'booking/dialogs/destination.html',
        {
            'cargo': cargo,
            'locations': available_destinations,
            'destination_value': value,
            'destination_error': error,
        },
    )


def _updated_rows(request: HttpRequest, dashboard: CargoDashboard) -> HttpResponse:
    return render(
        request,
        'booking/dialogs/_updated_rows.html',
        {'not_routed_cargos': dashboard.get_dashboard().not_routed_cargos},
    )


def create_booking_dialog_views(
    dashboard: CargoDashboard,
    specification: CargoSpecification,
    list_shipping_locations: Callable[[], list[Location]],
) -> tuple[
    Callable[[HttpRequest, str], HttpResponse],
    Callable[[HttpRequest, str], HttpResponse],
]:
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo_id, cargo = _find_cargo(dashboard, tracking_id)
        locations = list_shipping_locations()

        if request.method != 'POST':
            return _destination_dialog(request, cargo, locations)

        value = request.POST.get('destination', '')
        destination = next(
            (location for location in locations if location.unlocode.value == value),
            None,
        )
        if destination is None:
            return _destination_dialog(
                request, cargo, locations, value, 'Select a valid destination.'
            )
        try:
            specification.change_destination(cargo_id, destination)
        except ValueError:
            return _destination_dialog(
                request, cargo, locations, value, 'Destination must differ from origin.'
            )
        return _updated_rows(request, dashboard)

    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo_id, cargo = _find_cargo(dashboard, tracking_id)
        if request.method != 'POST':
            return render(
                request,
                'booking/dialogs/deadline.html',
                {
                    'cargo': cargo,
                    'deadline_value': cargo.route_specification.arrival_deadline.date().isoformat(),
                    'deadline_error': '',
                },
            )

        value = request.POST.get('deadline', '')
        try:
            deadline = date.fromisoformat(value)
        except ValueError:
            return render(
                request,
                'booking/dialogs/deadline.html',
                {
                    'cargo': cargo,
                    'deadline_value': value,
                    'deadline_error': 'Enter a valid arrival deadline.',
                },
            )

        specification.change_deadline(
            cargo_id,
            datetime.combine(deadline, time.min, tzinfo=UTC),
        )
        return _updated_rows(request, dashboard)

    return destination_dialog, deadline_dialog
