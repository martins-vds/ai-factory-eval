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


def _find_cargo(cargo_dashboard: CargoDashboard, tracking_id: str) -> Cargo:
    cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
    if cargo is None:
        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
    return cargo


def _completion_response(request: HttpRequest) -> HttpResponse:
    if request.headers.get('HX-Request') == 'true':
        return HttpResponse(status=204, headers={'HX-Redirect': '/admin/dashboard/'})
    return redirect('/admin/dashboard/')


def create_dialog_views(
    specification: CargoSpecification,
    cargo_dashboard: CargoDashboard,
    list_shipping_locations: Callable[[], list[Location]],
) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = _find_cargo(cargo_dashboard, tracking_id)
        locations = list_shipping_locations()
        excluded_codes = {
            cargo.route_specification.origin.unlocode.value,
            cargo.route_specification.destination.unlocode.value,
        }
        destinations = [
            location for location in locations if location.unlocode.value not in excluded_codes
        ]
        destination_value = request.POST.get('destination', '')
        destination_error = ''

        if request.method == 'POST':
            destination = next(
                (
                    location
                    for location in destinations
                    if location.unlocode.value == destination_value
                ),
                None,
            )
            if destination is None:
                destination_error = 'Select a valid destination.'
            else:
                try:
                    specification.change_destination(TrackingId(tracking_id), destination)
                except LookupError as error:
                    raise Http404(str(error)) from error
                return _completion_response(request)

        return render(
            request,
            'booking/dialogs/destination.html',
            {
                'cargo': cargo,
                'destinations': destinations,
                'destination_value': destination_value,
                'destination_error': destination_error,
            },
        )

    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = _find_cargo(cargo_dashboard, tracking_id)
        deadline_value = (
            request.POST.get('deadline', '')
            if request.method == 'POST'
            else cargo.route_specification.arrival_deadline.strftime('%Y-%m-%d')
        )
        deadline_error = ''

        if request.method == 'POST':
            try:
                arrival_deadline = datetime.combine(date.fromisoformat(deadline_value), time.min)
            except ValueError:
                deadline_error = (
                    'Choose an arrival deadline.'
                    if not deadline_value
                    else 'Enter a valid arrival deadline.'
                )
            else:
                try:
                    specification.change_deadline(
                        TrackingId(tracking_id),
                        timezone.make_aware(arrival_deadline),
                    )
                except LookupError as error:
                    raise Http404(str(error)) from error
                return _completion_response(request)

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
