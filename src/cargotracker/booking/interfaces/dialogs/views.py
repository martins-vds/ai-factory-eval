from collections.abc import Callable
from datetime import UTC, date, datetime, time

from django.http import Http404, HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import redirect, render

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.cargo.domain.cargo import Cargo
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location


def _find_cargo(cargo_dashboard: CargoDashboard, tracking_id: str) -> Cargo:
    cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
    if cargo is None:
        raise Http404
    return cargo


def _destination_context(
    cargo: Cargo,
    locations: list[Location],
    destination_error: str = '',
) -> dict[str, object]:
    origin = cargo.route_specification.origin
    destination = cargo.route_specification.destination
    potential_destinations = [
        location for location in locations if location != origin and location != destination
    ]
    return {
        'cargo': cargo,
        'potential_destinations': potential_destinations,
        'destination_error': destination_error,
    }


def _deadline_context(cargo: Cargo, deadline_error: str = '') -> dict[str, object]:
    return {
        'cargo': cargo,
        'deadline_value': cargo.route_specification.arrival_deadline.date().isoformat(),
        'deadline_error': deadline_error,
    }


def _refreshed_not_routed_table(
    request: HttpRequest, cargo_dashboard: CargoDashboard
) -> HttpResponse:
    cargos = cargo_dashboard.get_dashboard()
    response = render(
        request,
        'booking/dashboard/not_routed_table.html',
        {'not_routed_cargos': cargos.not_routed_cargos},
    )
    response['HX-Retarget'] = '#not-routed-cargo'
    response['HX-Reswap'] = 'outerHTML'
    return response


def _render_dialog(
    request: HttpRequest, template_name: str, context: dict[str, object]
) -> HttpResponse:
    if request.headers.get('HX-Request') == 'true':
        return render(request, template_name, {**context, 'is_dialog': True})
    return render(
        request,
        'booking/dialogs/edit_page.html',
        {**context, 'dialog_template': template_name, 'is_dialog': False},
    )


def _after_update(request: HttpRequest, cargo_dashboard: CargoDashboard) -> HttpResponse:
    if request.headers.get('HX-Request') == 'true':
        return _refreshed_not_routed_table(request, cargo_dashboard)
    return redirect('/admin/dashboard/')


def create_dialog_views(
    cargo_dashboard: CargoDashboard,
    cargo_specification: CargoSpecification,
    list_shipping_locations: Callable[[], list[Location]],
) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        if request.method not in {'GET', 'POST'}:
            return HttpResponseNotAllowed(['GET', 'POST'])

        cargo = _find_cargo(cargo_dashboard, tracking_id)
        locations = list_shipping_locations()
        context = _destination_context(cargo, locations)
        potential_destinations = context['potential_destinations']
        if request.method == 'GET':
            return _render_dialog(request, 'booking/dialogs/destination.html', context)

        destination_code = request.POST.get('destination', '')
        destination = next(
            (
                location
                for location in potential_destinations
                if location.unlocode.value == destination_code
            ),
            None,
        )
        if destination is None:
            context['destination_error'] = 'Select a valid destination.'
            return _render_dialog(request, 'booking/dialogs/destination.html', context)

        try:
            cargo_specification.change_destination(TrackingId(tracking_id), destination)
        except LookupError as error:
            raise Http404 from error
        return _after_update(request, cargo_dashboard)

    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        if request.method not in {'GET', 'POST'}:
            return HttpResponseNotAllowed(['GET', 'POST'])

        cargo = _find_cargo(cargo_dashboard, tracking_id)
        context = _deadline_context(cargo)
        if request.method == 'GET':
            return _render_dialog(request, 'booking/dialogs/deadline.html', context)

        try:
            deadline = date.fromisoformat(request.POST.get('deadline', ''))
        except ValueError:
            context['deadline_error'] = 'Enter a valid arrival deadline.'
            return _render_dialog(request, 'booking/dialogs/deadline.html', context)

        try:
            cargo_specification.change_deadline(
                TrackingId(tracking_id),
                datetime.combine(deadline, time.min, tzinfo=UTC),
            )
        except LookupError as error:
            raise Http404 from error
        return _after_update(request, cargo_dashboard)

    return destination_dialog, deadline_dialog
