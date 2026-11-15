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


def _dialog_response(
    request: HttpRequest, template: str, context: dict[str, object]
) -> HttpResponse:
    if request.headers.get('HX-Request') == 'true':
        template = f'booking/dialogs/_{template}_form.html'
    else:
        template = f'booking/dialogs/{template}.html'
    return render(request, template, context)


def _find_cargo(cargo_dashboard: CargoDashboard, tracking_id: str) -> Cargo:
    cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
    if cargo is None:
        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
    return cargo


def _complete_dialog(request: HttpRequest) -> HttpResponse:
    if request.headers.get('HX-Request') == 'true':
        response = HttpResponse(status=204)
        response['HX-Redirect'] = '/admin/dashboard/'
        return response
    return redirect('/admin/dashboard/')


def create_booking_dialog_views(
    specification: CargoSpecification,
    cargo_dashboard: CargoDashboard,
    list_shipping_locations: Callable[[], list[Location]],
) -> tuple[
    Callable[[HttpRequest, str], HttpResponse],
    Callable[[HttpRequest, str], HttpResponse],
]:
    def change_destination(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = _find_cargo(cargo_dashboard, tracking_id)
        locations = list_shipping_locations()
        available_destinations = [
            location
            for location in locations
            if location
            not in (
                cargo.route_specification.origin,
                cargo.route_specification.destination,
            )
        ]
        context = {
            'cargo': cargo,
            'locations': available_destinations,
            'form_action': f'/admin/cargo/{tracking_id}/destination/',
            'destination_error': '',
        }

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
                context['destination_error'] = 'Select a valid destination.'
            else:
                try:
                    specification.change_destination(TrackingId(tracking_id), destination)
                except LookupError as error:
                    raise Http404(str(error)) from error
                return _complete_dialog(request)

        return _dialog_response(request, 'destination', context)

    def change_deadline(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = _find_cargo(cargo_dashboard, tracking_id)
        deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
        context = {
            'cargo': cargo,
            'deadline_value': deadline_value,
            'form_action': f'/admin/cargo/{tracking_id}/deadline/',
            'deadline_error': '',
        }

        if request.method == 'POST':
            deadline_value = request.POST.get('deadline', '')
            context['deadline_value'] = deadline_value
            try:
                deadline = date.fromisoformat(deadline_value)
            except ValueError:
                context['deadline_error'] = 'Enter a valid arrival deadline.'
            else:
                arrival_deadline = timezone.make_aware(datetime.combine(deadline, time.min))
                try:
                    specification.change_deadline(TrackingId(tracking_id), arrival_deadline)
                except LookupError as error:
                    raise Http404(str(error)) from error
                return _complete_dialog(request)

        return _dialog_response(request, 'deadline', context)

    return change_destination, change_deadline
