from collections.abc import Callable
from datetime import date, datetime, time

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.cargo.domain.cargo import Cargo
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location


def _not_routed_table(
    request: HttpRequest, cargo_dashboard: CargoDashboard
) -> HttpResponse:
    return render(
        request,
        'booking/dashboard/not_routed_table.html',
        {'not_routed_cargos': cargo_dashboard.get_dashboard().not_routed_cargos},
    )


def _destination_context(
    cargo: Cargo, locations: list[Location], error: str = ''
) -> dict[str, object]:
    return {
        'cargo': cargo,
        'locations': [
            location
            for location in locations
            if location not in (
                cargo.route_specification.origin,
                cargo.route_specification.destination,
            )
        ],
        'destination_error': error,
    }


def create_booking_dialog_views(
    cargo_specification: CargoSpecification,
    cargo_dashboard: CargoDashboard,
    find_locations: Callable[[], list[Location]],
) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
        if cargo is None:
            return render(
                request,
                'booking/dialogs/error.html',
                {'tracking_id': tracking_id},
                status=404,
            )

        if request.method == 'POST':
            destination_code = request.POST.get('destination', '')
            locations = find_locations()
            destinations = _destination_context(cargo, locations)['locations']
            destination = next(
                (
                    location for location in destinations if location.unlocode.value == destination_code
                ),
                None,
            )
            if destination is None:
                return render(
                    request,
                    'booking/dialogs/destination.html',
                    _destination_context(cargo, locations, 'Select a valid destination.'),
                )

            cargo_specification.change_destination(cargo.tracking_id, destination)
            response = _not_routed_table(request, cargo_dashboard)
            response['HX-Retarget'] = '#not-routed-cargo'
            response['HX-Reswap'] = 'outerHTML'
            return response

        return render(
            request,
            'booking/dialogs/destination.html',
            _destination_context(cargo, find_locations()),
        )

    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
        if cargo is None:
            return render(
                request,
                'booking/dialogs/error.html',
                {'tracking_id': tracking_id},
                status=404,
            )

        deadline = cargo.route_specification.arrival_deadline.date()
        if request.method == 'POST':
            deadline_value = request.POST.get('deadline', '')
            try:
                deadline = date.fromisoformat(deadline_value)
            except ValueError:
                return render(
                    request,
                    'booking/dialogs/deadline.html',
                    {
                        'cargo': cargo,
                        'deadline': deadline_value,
                        'deadline_error': 'Enter a valid arrival deadline.',
                    },
                )

            cargo_specification.change_deadline(
                cargo.tracking_id,
                timezone.make_aware(datetime.combine(deadline, time.min)),
            )
            response = _not_routed_table(request, cargo_dashboard)
            response['HX-Retarget'] = '#not-routed-cargo'
            response['HX-Reswap'] = 'outerHTML'
            return response

        return render(
            request,
            'booking/dialogs/deadline.html',
            {'cargo': cargo, 'deadline': deadline},
        )

    return destination_dialog, deadline_dialog
