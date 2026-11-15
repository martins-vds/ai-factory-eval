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


def _find_cargo(cargo_dashboard: CargoDashboard, tracking_id: TrackingId) -> Cargo:
    cargo = cargo_dashboard.get_cargo_details(tracking_id)
    if cargo is None:
        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
    return cargo


def _complete_dialog(request: HttpRequest) -> HttpResponse:
    if request.headers.get('HX-Request') == 'true':
        return HttpResponse('', headers={'HX-Redirect': '/admin/dashboard/'})
    return redirect('/admin/dashboard/')


def create_dialog_views(
    cargo_dashboard: CargoDashboard,
    cargo_specification: CargoSpecification,
    list_shipping_locations: Callable[[], list[Location]],
) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        tracking = TrackingId(tracking_id)
        cargo = _find_cargo(cargo_dashboard, tracking)
        locations = list(list_shipping_locations())
        destinations = [
            location
            for location in locations
            if location
            not in (
                cargo.route_specification.origin,
                cargo.route_specification.destination,
            )
        ]
        selected_destination = request.POST.get('destination', '')
        error = ''

        if request.method == 'POST':
            destination = next(
                (
                    location
                    for location in destinations
                    if location.unlocode.value == selected_destination
                ),
                None,
            )
            if destination is None:
                error = 'Select a valid destination.'
            else:
                try:
                    cargo_specification.change_destination(tracking, destination)
                except LookupError as exc:
                    raise Http404(str(exc)) from exc
                return _complete_dialog(request)

        return render(
            request,
            'booking/dialogs/destination.html',
            {
                'cargo': cargo,
                'destinations': destinations,
                'selected_destination': selected_destination,
                'error': error,
                'action_url': f'/admin/cargo/{tracking_id}/destination/',
            },
        )

    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        tracking = TrackingId(tracking_id)
        cargo = _find_cargo(cargo_dashboard, tracking)
        deadline_value = request.POST.get('deadline', '')
        if request.method != 'POST':
            deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
        error = ''

        if request.method == 'POST':
            try:
                parsed_deadline = date.fromisoformat(deadline_value)
                if parsed_deadline.isoformat() != deadline_value:
                    raise ValueError
            except ValueError:
                error = 'Enter a valid arrival deadline.'
            else:
                arrival_deadline = timezone.make_aware(datetime.combine(parsed_deadline, time.min))
                try:
                    cargo_specification.change_deadline(tracking, arrival_deadline)
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
                'action_url': f'/admin/cargo/{tracking_id}/deadline/',
            },
        )

    return destination_dialog, deadline_dialog
