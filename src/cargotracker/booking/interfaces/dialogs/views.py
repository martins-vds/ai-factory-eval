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


def _cargo_for_dialog(cargo_dashboard: CargoDashboard, tracking_id: str) -> Cargo:
    cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
    if cargo is None:
        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
    return cargo


def _updated_response(request: HttpRequest) -> HttpResponse:
    if request.headers.get('HX-Request') == 'true':
        return HttpResponse(status=204, headers={'HX-Redirect': '/admin/dashboard/'})
    return redirect('/admin/dashboard/')


def _destination_context(
    cargo: Cargo,
    locations: list[Location],
    destination_error: str = '',
) -> dict[str, object]:
    available_locations = [
        location
        for location in locations
        if location != cargo.route_specification.origin
        and location != cargo.route_specification.destination
    ]
    return {
        'cargo': cargo,
        'locations': available_locations,
        'destination_error': destination_error,
    }


def _deadline_context(cargo: Cargo, deadline_value: str = '', deadline_error: str = '') -> dict:
    return {
        'cargo': cargo,
        'deadline_value': deadline_value
        or cargo.route_specification.arrival_deadline.date().isoformat(),
        'deadline_error': deadline_error,
    }


def create_dialog_views(
    cargo_dashboard: CargoDashboard,
    specification: CargoSpecification,
    list_shipping_locations: Callable[[], list[Location]],
) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = _cargo_for_dialog(cargo_dashboard, tracking_id)
        locations = list(list_shipping_locations())
        if request.method == 'POST':
            destination = next(
                (
                    location
                    for location in locations
                    if location.unlocode.value == request.POST.get('destination')
                    and location != cargo.route_specification.origin
                    and location != cargo.route_specification.destination
                ),
                None,
            )
            if destination is None:
                context = _destination_context(
                    cargo,
                    locations,
                    'Select a valid destination.',
                )
                return render(request, 'booking/dialogs/destination.html', context)
            specification.change_destination(cargo.tracking_id, destination)
            return _updated_response(request)

        return render(
            request,
            'booking/dialogs/destination.html',
            _destination_context(cargo, locations),
        )

    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = _cargo_for_dialog(cargo_dashboard, tracking_id)
        if request.method == 'POST':
            deadline_value = request.POST.get('deadline', '')
            try:
                deadline = date.fromisoformat(deadline_value)
            except ValueError:
                return render(
                    request,
                    'booking/dialogs/deadline.html',
                    _deadline_context(cargo, deadline_value, 'Enter a valid arrival deadline.'),
                )
            specification.change_deadline(
                cargo.tracking_id,
                timezone.make_aware(datetime.combine(deadline, time.min)),
            )
            return _updated_response(request)

        return render(
            request,
            'booking/dialogs/deadline.html',
            _deadline_context(cargo),
        )

    return destination_dialog, deadline_dialog
