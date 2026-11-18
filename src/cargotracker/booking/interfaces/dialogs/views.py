from collections.abc import Callable
from datetime import datetime, time

from django.http import Http404, HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.utils import timezone

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location


def _dialog_completion_response(request: HttpRequest) -> HttpResponse:
    if request.headers.get('HX-Request') == 'true':
        response = HttpResponse(status=204)
        response['HX-Redirect'] = '/admin/dashboard/'
        return response
    return redirect('/admin/dashboard/')


def create_destination_dialog_view(
    cargo_dashboard: CargoDashboard,
    specification: CargoSpecification,
    list_shipping_locations: Callable[[], list[Location]],
) -> Callable[[HttpRequest, str], HttpResponse]:
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        if request.method not in {'GET', 'POST'}:
            return HttpResponseNotAllowed(['GET', 'POST'])

        cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
        if cargo is None:
            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
        available_locations = list(list_shipping_locations())
        locations = [
            location
            for location in available_locations
            if location not in (
                cargo.route_specification.origin,
                cargo.route_specification.destination,
            )
        ]
        selected_destination = request.POST.get('destination', '')
        if request.method == 'POST':
            destination_by_code = {
                location.unlocode.value: location for location in locations
            }
            destination = destination_by_code.get(selected_destination)
            if destination is None:
                return render(
                    request,
                    'booking/dialogs/destination.html',
                    {
                        'cargo': cargo,
                        'locations': locations,
                        'selected_destination': selected_destination,
                        'destination_error': 'Select an available destination.',
                    },
                )
            specification.change_destination(cargo.tracking_id, destination)
            return _dialog_completion_response(request)

        return render(
            request,
            'booking/dialogs/destination.html',
            {
                'cargo': cargo,
                'locations': locations,
                'selected_destination': selected_destination,
            },
        )

    return destination_dialog


def create_deadline_dialog_view(
    cargo_dashboard: CargoDashboard,
    specification: CargoSpecification,
) -> Callable[[HttpRequest, str], HttpResponse]:
    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        if request.method not in {'GET', 'POST'}:
            return HttpResponseNotAllowed(['GET', 'POST'])

        cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
        if cargo is None:
            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
        deadline_value = (
            request.POST.get('deadline', '')
            if request.method == 'POST'
            else timezone.localtime(cargo.route_specification.arrival_deadline).strftime(
                '%Y-%m-%d'
            )
        )
        deadline_error = ''
        if request.method == 'POST':
            try:
                arrival_deadline = datetime.strptime(deadline_value, '%Y-%m-%d').date()
            except ValueError:
                deadline_error = 'Enter a valid arrival deadline.'
            else:
                specification.change_deadline(
                    cargo.tracking_id,
                    timezone.make_aware(datetime.combine(arrival_deadline, time.min)),
                )
                return _dialog_completion_response(request)

        return render(
            request,
            'booking/dialogs/deadline.html',
            {
                'cargo': cargo,
                'deadline_value': deadline_value,
                'deadline_error': deadline_error,
            },
        )

    return deadline_dialog
