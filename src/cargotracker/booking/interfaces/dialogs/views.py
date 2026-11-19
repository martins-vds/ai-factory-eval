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


def _updated_table(request: HttpRequest, cargo_dashboard: CargoDashboard) -> HttpResponse:
    if request.headers.get('HX-Request') != 'true':
        return redirect('/admin/dashboard/')
    cargos = cargo_dashboard.get_dashboard()
    response = render(
        request,
        'booking/dashboard/not_routed_table.html',
        {'not_routed_cargos': cargos.not_routed_cargos},
    )
    response['HX-Retarget'] = '#not-routed-cargo'
    response['HX-Reswap'] = 'outerHTML'
    return response


def _destination_context(
    cargo: Cargo,
    tracking_id: str,
    locations: list[Location],
    destination_value: str = '',
    destination_error: str = '',
) -> dict[str, object]:
    destinations = [
        location
        for location in locations
        if location not in (cargo.route_specification.origin, cargo.route_specification.destination)
    ]
    if not destination_value and destinations:
        destination_value = next(
            (location.unlocode.value for location in destinations if location.unlocode.value == 'SEGOT'),
            destinations[0].unlocode.value,
        )
    return {
        'cargo': cargo,
        'destinations': destinations,
        'destination_value': destination_value,
        'destination_error': destination_error,
        'action': f'/admin/cargo/{tracking_id}/destination/',
    }


def create_dialog_views(
    cargo_specification: CargoSpecification,
    cargo_dashboard: CargoDashboard,
    list_shipping_locations: Callable[[], list[Location]],
) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = _find_cargo(cargo_dashboard, tracking_id)
        locations = list(list_shipping_locations())
        destination_value = request.POST.get('destination', '')
        destination_error = ''

        if request.method == 'POST':
            context = _destination_context(
                cargo, tracking_id, locations, destination_value=destination_value
            )
            destination = next(
                (
                    location
                    for location in context['destinations']
                    if location.unlocode.value == destination_value
                ),
                None,
            )
            if destination is None:
                destination_error = 'Select a valid destination.'
            else:
                cargo_specification.change_destination(TrackingId(tracking_id), destination)
                return _updated_table(request, cargo_dashboard)

        context = _destination_context(
            cargo,
            tracking_id,
            locations,
            destination_value=destination_value,
            destination_error=destination_error,
        )
        return render(request, 'booking/dialogs/destination.html', context)

    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = _find_cargo(cargo_dashboard, tracking_id)
        deadline_value = request.POST.get(
            'deadline', cargo.route_specification.arrival_deadline.date().isoformat()
        )
        deadline_error = ''

        if request.method == 'POST':
            try:
                arrival_date = date.fromisoformat(deadline_value)
            except ValueError:
                deadline_error = 'Enter a valid arrival deadline.'
            else:
                arrival_deadline = timezone.make_aware(
                    datetime.combine(arrival_date, time.min),
                )
                cargo_specification.change_deadline(TrackingId(tracking_id), arrival_deadline)
                return _updated_table(request, cargo_dashboard)

        return render(
            request,
            'booking/dialogs/deadline.html',
            {
                'cargo': cargo,
                'deadline_value': deadline_value,
                'deadline_error': deadline_error,
                'action': f'/admin/cargo/{tracking_id}/deadline/',
            },
        )

    return destination_dialog, deadline_dialog
