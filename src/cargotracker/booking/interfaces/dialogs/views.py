from collections.abc import Callable
from datetime import date, datetime, time

from django.http import Http404, HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.utils import timezone

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.cargo.domain.cargo import Cargo
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location


def _find_cargo(cargo_dashboard: CargoDashboard, tracking_id: str) -> Cargo:
    cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
    if cargo is None:
        raise Http404
    return cargo


def _not_found(request: HttpRequest, tracking_id: str) -> HttpResponse:
    return render(
        request,
        'booking/dialogs/not_found.html',
        {'tracking_id': tracking_id},
        status=404,
    )


def _destination_context(
    cargo: Cargo,
    locations: list[Location],
    error: str = '',
) -> dict[str, object]:
    return {
        'cargo': cargo,
        'destinations': [
            location
            for location in locations
            if location
            not in (cargo.route_specification.origin, cargo.route_specification.destination)
        ],
        'destination_error': error,
    }


def _deadline_context(cargo: Cargo, value: str | None = None, error: str = '') -> dict[str, object]:
    deadline_value = (
        timezone.localtime(cargo.route_specification.arrival_deadline).date().isoformat()
        if value is None
        else value
    )
    return {
        'cargo': cargo,
        'deadline_value': deadline_value,
        'deadline_error': error,
    }


def _successful_update(request: HttpRequest) -> HttpResponse:
    if request.headers.get('HX-Request') != 'true':
        return redirect('/admin/dashboard/')
    response = HttpResponse(status=204)
    response['HX-Trigger'] = 'cargoUpdated'
    return response


def create_dialog_views(
    cargo_dashboard: CargoDashboard,
    cargo_specification: CargoSpecification,
    list_shipping_locations: Callable[[], list[Location]],
) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        try:
            cargo = _find_cargo(cargo_dashboard, tracking_id)
        except Http404:
            return _not_found(request, tracking_id)

        locations = list_shipping_locations()
        if request.method == 'POST':
            destination_code = request.POST.get('destination')
            destinations = {
                location.unlocode.value: location
                for location in locations
                if location
                not in (cargo.route_specification.origin, cargo.route_specification.destination)
            }
            destination = destinations.get(destination_code)
            if destination is None:
                context = _destination_context(
                    cargo,
                    locations,
                    'Select a valid destination.',
                )
                return render(
                    request,
                    'booking/dialogs/destination.html',
                    context,
                    status=400,
                )

            try:
                cargo_specification.change_destination(cargo.tracking_id, destination)
            except LookupError:
                return _not_found(request, tracking_id)
            return _successful_update(request)

        if request.method != 'GET':
            return HttpResponseNotAllowed(['GET', 'POST'])
        return render(
            request,
            'booking/dialogs/destination.html',
            _destination_context(cargo, locations),
        )

    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        try:
            cargo = _find_cargo(cargo_dashboard, tracking_id)
        except Http404:
            return _not_found(request, tracking_id)

        if request.method == 'POST':
            deadline_value = request.POST.get('deadline', '')
            try:
                deadline = datetime.combine(
                    date.fromisoformat(deadline_value),
                    time.min,
                )
            except ValueError:
                context = _deadline_context(
                    cargo,
                    deadline_value,
                    'Enter a valid arrival deadline.',
                )
                return render(
                    request,
                    'booking/dialogs/deadline.html',
                    context,
                    status=400,
                )

            try:
                cargo_specification.change_deadline(
                    cargo.tracking_id,
                    timezone.make_aware(deadline),
                )
            except LookupError:
                return _not_found(request, tracking_id)
            return _successful_update(request)

        if request.method != 'GET':
            return HttpResponseNotAllowed(['GET', 'POST'])
        return render(
            request,
            'booking/dialogs/deadline.html',
            _deadline_context(cargo),
        )

    return destination_dialog, deadline_dialog
