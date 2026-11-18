from collections.abc import Callable

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location


def _cargo_for_dialog(cargo_dashboard: CargoDashboard, tracking_id: str):
    try:
        cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
    except (TypeError, ValueError) as error:
        raise Http404(f'Cargo with tracking ID {tracking_id} not found.') from error
    if cargo is None:
        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
    return cargo


def _dialog_success(request: HttpRequest) -> HttpResponse:
    if request.headers.get('HX-Request') == 'true':
        response = HttpResponse()
        response['HX-Redirect'] = '/admin/dashboard/'
        return response
    return redirect('/admin/dashboard/')


def create_destination_dialog_view(
    cargo_dashboard: CargoDashboard,
    cargo_specification: CargoSpecification,
    list_shipping_locations: Callable[[], list[Location]],
) -> Callable[[HttpRequest, str], HttpResponse]:
    @require_http_methods(['GET', 'POST'])
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = _cargo_for_dialog(cargo_dashboard, tracking_id)
        cargo_tracking_id = TrackingId(tracking_id)
        locations = list_shipping_locations()
        available_destinations = [
            location
            for location in locations
            if location != cargo.route_specification.origin
            and location != cargo.route_specification.destination
        ]
        error = ''

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
                error = 'Select a valid destination.'
            else:
                cargo_specification.change_destination(cargo_tracking_id, destination)
                return _dialog_success(request)

        return render(
            request,
            'booking/dialogs/destination.html',
            {
                'cargo': cargo,
                'available_destinations': available_destinations,
                'error': error,
            },
        )

    return destination_dialog
