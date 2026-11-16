from collections.abc import Callable
from datetime import date, datetime, time

from django.http import Http404, HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render
from django.utils import timezone

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.cargo.domain.cargo import Cargo
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location


def _find_cargo(dashboard: CargoDashboard, tracking_id: str) -> Cargo:
    cargo = dashboard.get_cargo_details(TrackingId(tracking_id))
    if cargo is None:
        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
    return cargo


def _not_routed_table(request: HttpRequest, dashboard: CargoDashboard) -> HttpResponse:
    response = render(
        request,
        'booking/dashboard/not_routed_table.html',
        {'not_routed_cargos': dashboard.get_dashboard().not_routed_cargos},
    )
    response['HX-Retarget'] = '#not-routed-cargo'
    response['HX-Reswap'] = 'outerHTML'
    response['HX-Trigger'] = 'booking-dialog-complete'
    return response


def create_booking_dialog_views(
    cargo_specification: CargoSpecification,
    cargo_dashboard: CargoDashboard,
    list_shipping_locations: Callable[[], list[Location]],
) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        if request.method not in {'GET', 'POST'}:
            return HttpResponseNotAllowed(['GET', 'POST'])
        cargo = _find_cargo(cargo_dashboard, tracking_id)
        locations = list(list_shipping_locations())
        available_locations = [
            location
            for location in locations
            if location
            not in (cargo.route_specification.origin, cargo.route_specification.destination)
        ]
        selected_destination = None
        error = ''
        if request.method == 'POST':
            selected_destination = next(
                (
                    location
                    for location in available_locations
                    if location.unlocode.value == request.POST.get('destination')
                ),
                None,
            )
            if selected_destination is None:
                error = 'Select a valid destination.'
            else:
                try:
                    cargo_specification.change_destination(
                        TrackingId(tracking_id), selected_destination
                    )
                except LookupError as exception:
                    raise Http404(str(exception)) from exception
                return _not_routed_table(request, cargo_dashboard)

        return render(
            request,
            'booking/dialogs/destination.html',
            {
                'cargo': cargo,
                'locations': available_locations,
                'selected_destination': selected_destination,
                'destination_error': error,
            },
        )

    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        if request.method not in {'GET', 'POST'}:
            return HttpResponseNotAllowed(['GET', 'POST'])
        cargo = _find_cargo(cargo_dashboard, tracking_id)
        deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
        deadline_error = ''
        if request.method == 'POST':
            deadline_value = request.POST.get('deadline', '')
            try:
                selected_deadline = date.fromisoformat(deadline_value)
            except ValueError:
                deadline_error = 'Enter a valid date.'
            else:
                try:
                    cargo_specification.change_deadline(
                        TrackingId(tracking_id),
                        timezone.make_aware(datetime.combine(selected_deadline, time.min)),
                    )
                except LookupError as exception:
                    raise Http404(str(exception)) from exception
                return _not_routed_table(request, cargo_dashboard)

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
