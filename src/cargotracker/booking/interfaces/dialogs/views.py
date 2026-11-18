from collections.abc import Callable
from datetime import UTC, datetime, time

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location


def _find_cargo(cargo_dashboard: CargoDashboard, tracking_id: str):
    cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
    if cargo is None:
        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
    return cargo


def _render_not_routed_table(request: HttpRequest, cargo_dashboard: CargoDashboard) -> HttpResponse:
    if request.headers.get('HX-Request') != 'true':
        return redirect('/admin/dashboard/')
    response = render(
        request,
        'booking/dashboard/not_routed_table.html',
        {'not_routed_cargos': cargo_dashboard.get_dashboard().not_routed_cargos},
    )
    response['HX-Retarget'] = '#not-routed-cargo'
    response['HX-Reswap'] = 'outerHTML'
    return response


def create_destination_dialog_view(
    cargo_dashboard: CargoDashboard,
    list_shipping_locations: Callable[[], list[Location]],
) -> Callable[[HttpRequest, str], HttpResponse]:
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = _find_cargo(cargo_dashboard, tracking_id)
        locations = list_shipping_locations()
        destination_options = [
            location
            for location in locations
            if location not in (
                cargo.route_specification.origin,
                cargo.route_specification.destination,
            )
        ]
        return render(
            request,
            'booking/dialogs/destination.html',
            {'cargo': cargo, 'destination_options': destination_options},
        )

    return destination_dialog


def create_deadline_dialog_view(
    cargo_dashboard: CargoDashboard,
    cargo_specification: CargoSpecification,
) -> Callable[[HttpRequest, str], HttpResponse]:
    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = _find_cargo(cargo_dashboard, tracking_id)
        deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
        deadline_error = ''
        if request.method == 'POST':
            try:
                arrival_date = datetime.strptime(request.POST.get('deadline', ''), '%Y-%m-%d')
            except ValueError:
                deadline_error = 'Enter a valid arrival deadline.'
            else:
                try:
                    cargo_specification.change_deadline(
                        TrackingId(tracking_id),
                        datetime.combine(arrival_date.date(), time.min, tzinfo=UTC),
                    )
                except LookupError as error:
                    raise Http404(str(error)) from error
                return _render_not_routed_table(request, cargo_dashboard)
        return render(
            request,
            'booking/dialogs/deadline.html',
            {
                'cargo': cargo,
                'deadline_value': request.POST.get('deadline', deadline_value),
                'deadline_error': deadline_error,
            },
        )

    return deadline_dialog
