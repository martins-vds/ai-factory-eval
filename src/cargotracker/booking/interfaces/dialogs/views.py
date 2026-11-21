from collections.abc import Callable
from datetime import date, datetime, time

from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render
from django.utils import timezone

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.cargo.domain.cargo import Cargo
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location


def _find_cargo(cargo_dashboard: CargoDashboard, tracking_id: str) -> Cargo | None:
    try:
        return cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
    except ValueError:
        return None


def _destination_options(cargo: Cargo, locations: list[Location]) -> list[Location]:
    return [
        location
        for location in locations
        if location not in (cargo.route_specification.origin, cargo.route_specification.destination)
    ]


def _not_found(request: HttpRequest, tracking_id: str) -> HttpResponse:
    return render(
        request,
        'booking/dialogs/not_found.html',
        {'tracking_id': tracking_id},
        status=404,
    )


def _destination_form(
    request: HttpRequest,
    cargo: Cargo,
    locations: list[Location],
    error: str,
) -> HttpResponse:
    return render(
        request,
        'booking/dialogs/destination.html',
        {
            'cargo': cargo,
            'destinations': _destination_options(cargo, locations),
            'error': error,
        },
    )


def _deadline_form(
    request: HttpRequest,
    cargo: Cargo,
    deadline_value: str,
    error: str,
) -> HttpResponse:
    return render(
        request,
        'booking/dialogs/deadline.html',
        {
            'cargo': cargo,
            'deadline_value': deadline_value,
            'error': error,
        },
    )


def create_dialog_views(
    cargo_dashboard: CargoDashboard,
    cargo_specification: CargoSpecification,
    list_shipping_locations: Callable[[], list[Location]],
) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        if request.method not in {'GET', 'POST'}:
            return HttpResponseNotAllowed(['GET', 'POST'])

        cargo = _find_cargo(cargo_dashboard, tracking_id)
        if cargo is None:
            return _not_found(request, tracking_id)

        locations = list_shipping_locations()
        if request.method == 'GET':
            return _destination_form(request, cargo, locations, '')

        selected_destination = request.POST.get('destination')
        destination = next(
            (
                location
                for location in _destination_options(cargo, locations)
                if location.unlocode.value == selected_destination
            ),
            None,
        )
        if destination is None:
            return _destination_form(
                request,
                cargo,
                locations,
                'Select a valid destination.',
            )

        cargo_specification.change_destination(cargo.tracking_id, destination)
        return HttpResponse(status=204, headers={'HX-Redirect': '/admin/dashboard/'})

    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        if request.method not in {'GET', 'POST'}:
            return HttpResponseNotAllowed(['GET', 'POST'])

        cargo = _find_cargo(cargo_dashboard, tracking_id)
        if cargo is None:
            return _not_found(request, tracking_id)

        if request.method == 'GET':
            return _deadline_form(
                request,
                cargo,
                cargo.route_specification.arrival_deadline.date().isoformat(),
                '',
            )

        deadline_value = request.POST.get('deadline', '')
        try:
            deadline = date.fromisoformat(deadline_value)
        except ValueError:
            return _deadline_form(
                request,
                cargo,
                deadline_value,
                'Enter a valid arrival deadline.',
            )

        arrival_deadline = timezone.make_aware(datetime.combine(deadline, time.min))
        cargo_specification.change_deadline(cargo.tracking_id, arrival_deadline)
        return HttpResponse(status=204, headers={'HX-Redirect': '/admin/dashboard/'})

    return destination_dialog, deadline_dialog
