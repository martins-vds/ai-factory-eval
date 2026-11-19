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
        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
    return cargo


def _complete_dialog(request: HttpRequest) -> HttpResponse:
    if request.headers.get('HX-Request') == 'true':
        return HttpResponse(status=204, headers={'HX-Redirect': '/admin/dashboard/'})
    return redirect('/admin/dashboard/')


def _destination_context(
    cargo: Cargo,
    locations: list[Location],
    destination_value: str = '',
    error: str = '',
) -> dict[str, object]:
    origin = cargo.route_specification.origin
    current_destination = cargo.route_specification.destination
    return {
        'cargo': cargo,
        'destinations': [
            location
            for location in locations
            if location != origin and location != current_destination
        ],
        'destination_value': destination_value,
        'error': error,
    }


def create_booking_dialog_views(
    cargo_dashboard: CargoDashboard,
    specification: CargoSpecification,
    list_shipping_locations: Callable[[], list[Location]],
) -> tuple[
    Callable[[HttpRequest, str], HttpResponse],
    Callable[[HttpRequest, str], HttpResponse],
]:
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        if request.method not in {'GET', 'POST'}:
            return HttpResponseNotAllowed(['GET', 'POST'])

        cargo = _find_cargo(cargo_dashboard, tracking_id)
        locations = list_shipping_locations()
        destination_value = request.POST.get('destination', '') if request.method == 'POST' else ''
        error = ''

        if request.method == 'POST':
            destination = next(
                (
                    location
                    for location in _destination_context(cargo, locations)['destinations']
                    if location.unlocode.value == destination_value
                ),
                None,
            )
            if destination is None:
                error = 'Select a valid destination.'
            else:
                try:
                    specification.change_destination(TrackingId(tracking_id), destination)
                except LookupError as exc:
                    raise Http404(str(exc)) from exc
                return _complete_dialog(request)

        return render(
            request,
            'booking/dialogs/destination.html',
            _destination_context(cargo, locations, destination_value, error),
        )

    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        if request.method not in {'GET', 'POST'}:
            return HttpResponseNotAllowed(['GET', 'POST'])

        cargo = _find_cargo(cargo_dashboard, tracking_id)
        deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
        error = ''

        if request.method == 'POST':
            deadline_value = request.POST.get('deadline', '')
            try:
                arrival_date = date.fromisoformat(deadline_value)
                if arrival_date.isoformat() != deadline_value:
                    raise ValueError('Enter an ISO arrival date.')
            except ValueError:
                error = 'Enter a valid arrival deadline.'
            else:
                arrival_deadline = timezone.make_aware(
                    datetime.combine(arrival_date, time.min),
                )
                try:
                    specification.change_deadline(TrackingId(tracking_id), arrival_deadline)
                except LookupError as exc:
                    raise Http404(str(exc)) from exc
                return _complete_dialog(request)

        return render(
            request,
            'booking/dialogs/deadline.html',
            {
                'cargo': cargo,
                'deadline_value': deadline_value,
                'error': error,
            },
        )

    return destination_dialog, deadline_dialog
