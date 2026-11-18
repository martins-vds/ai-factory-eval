from collections.abc import Callable
from datetime import date, datetime, time

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location


def _not_found_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
    message = f'Cargo with tracking ID {tracking_id} not found.'
    if request.headers.get('HX-Request') == 'true':
        return render(
            request,
            'booking/dialogs/_dialog_error.html',
            {'message': message},
            status=404,
        )
    raise Http404(message)


def create_deadline_dialog_view(
    cargo_dashboard: CargoDashboard,
    cargo_specification: CargoSpecification,
) -> Callable[[HttpRequest, str], HttpResponse]:
    @require_http_methods(['GET', 'POST'])
    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
        if cargo is None:
            return _not_found_dialog(request, tracking_id)

        deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
        deadline_error = None
        if request.method == 'POST':
            deadline_value = request.POST.get('deadline', '')
            try:
                deadline = date.fromisoformat(deadline_value)
                if deadline.isoformat() != deadline_value:
                    raise ValueError
            except ValueError:
                deadline_error = 'Enter a valid arrival deadline.'
            else:
                cargo_specification.change_deadline(
                    cargo.tracking_id,
                    timezone.make_aware(datetime.combine(deadline, time.min)),
                )
                if request.headers.get('HX-Request') == 'true':
                    return HttpResponse(status=204, headers={'HX-Redirect': '/admin/dashboard/'})
                return redirect('/admin/dashboard/')

        context = {
            'cargo': cargo,
            'deadline_value': deadline_value,
            'deadline_error': deadline_error,
            'tracking_id': tracking_id,
        }
        template = (
            'booking/dialogs/_deadline_dialog.html'
            if request.headers.get('HX-Request') == 'true'
            else 'booking/dialogs/deadline.html'
        )
        return render(request, template, context)

    return deadline_dialog


def create_destination_dialog_view(
    cargo_dashboard: CargoDashboard,
    cargo_specification: CargoSpecification,
    list_shipping_locations: Callable[[], list[Location]],
) -> Callable[[HttpRequest, str], HttpResponse]:
    @require_http_methods(['GET', 'POST'])
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
        if cargo is None:
            return _not_found_dialog(request, tracking_id)

        origin = cargo.route_specification.origin
        current_destination = cargo.route_specification.destination
        locations = [
            location
            for location in list_shipping_locations()
            if location not in (origin, current_destination)
        ]
        destination_error = None
        if request.method == 'POST':
            submitted_destination = request.POST.get('destination')
            destination = next(
                (
                    location
                    for location in locations
                    if location.unlocode.value == submitted_destination
                ),
                None,
            )
            if destination is None:
                destination_error = 'Choose a valid destination.'
            else:
                cargo_specification.change_destination(cargo.tracking_id, destination)
                if request.headers.get('HX-Request') == 'true':
                    return HttpResponse(status=204, headers={'HX-Redirect': '/admin/dashboard/'})
                return redirect('/admin/dashboard/')

        context = {
            'cargo': cargo,
            'current_destination': current_destination,
            'destination_error': destination_error,
            'locations': locations,
            'tracking_id': tracking_id,
        }
        template = (
            'booking/dialogs/_destination_dialog.html'
            if request.headers.get('HX-Request') == 'true'
            else 'booking/dialogs/destination.html'
        )
        return render(request, template, context)

    return destination_dialog
