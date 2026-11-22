from collections.abc import Callable
from datetime import date, datetime, time

from django.http import Http404, HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.utils import timezone

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location

_DIALOG_TEMPLATES = {
    'destination': 'booking/dialogs/destination_form.html',
    'deadline': 'booking/dialogs/deadline_form.html',
}


def _cargo_for_edit(cargo_dashboard: CargoDashboard, tracking_id: str):
    cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
    if cargo is None:
        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
    return cargo


def _render_dialog(
    request: HttpRequest,
    template: str,
    context: dict[str, object],
) -> HttpResponse:
    if request.headers.get('HX-Request') == 'true':
        return render(request, template, context)
    return render(
        request,
        'booking/dialogs/page.html',
        {'dialog_template': template, **context},
    )


def _refreshed_table(
    request: HttpRequest,
    cargo_dashboard: CargoDashboard,
) -> HttpResponse:
    if request.headers.get('HX-Request') != 'true':
        return redirect('/admin/dashboard/')
    dashboard = cargo_dashboard.get_dashboard()
    response = render(
        request,
        'booking/dashboard/not_routed_table.html',
        {'not_routed_cargos': dashboard.not_routed_cargos},
    )
    response.headers['HX-Retarget'] = '#not-routed-cargo'
    response.headers['HX-Reswap'] = 'outerHTML'
    return response


def _destination_context(
    cargo,
    locations: list[Location],
    selected_destination: str = '',
    error: str = '',
) -> dict[str, object]:
    origin = cargo.route_specification.origin
    destination = cargo.route_specification.destination
    return {
        'tracking_id': cargo.tracking_id.value,
        'origin': origin,
        'current_destination': destination,
        'destinations': [
            location
            for location in locations
            if location != origin and location != destination
        ],
        'selected_destination': selected_destination,
        'destination_error': error,
    }


def _deadline_context(cargo, deadline_value: str = '', error: str = '') -> dict[str, object]:
    deadline = cargo.route_specification.arrival_deadline
    if not deadline_value:
        deadline_value = deadline.strftime('%Y-%m-%d')
    return {
        'tracking_id': cargo.tracking_id.value,
        'origin': cargo.route_specification.origin,
        'destination': cargo.route_specification.destination,
        'deadline_value': deadline_value,
        'deadline_error': error,
    }


def create_booking_dialog_views(
    cargo_dashboard: CargoDashboard,
    cargo_specification: CargoSpecification,
    list_shipping_locations: Callable[[], list[Location]],
) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        if request.method not in {'GET', 'POST'}:
            return HttpResponseNotAllowed(['GET', 'POST'])
        cargo = _cargo_for_edit(cargo_dashboard, tracking_id)
        locations = list_shipping_locations()
        context = _destination_context(cargo, locations)

        if request.method == 'POST':
            selected_destination = request.POST.get('destination', '')
            options = {location.unlocode.value: location for location in context['destinations']}
            destination = options.get(selected_destination)
            if destination is None:
                context = _destination_context(
                    cargo,
                    locations,
                    selected_destination,
                    'Select a valid destination.',
                )
                return _render_dialog(
                    request,
                    _DIALOG_TEMPLATES['destination'],
                    context,
                )
            try:
                cargo_specification.change_destination(cargo.tracking_id, destination)
            except LookupError as error:
                raise Http404(str(error)) from error
            return _refreshed_table(request, cargo_dashboard)

        return _render_dialog(request, _DIALOG_TEMPLATES['destination'], context)

    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        if request.method not in {'GET', 'POST'}:
            return HttpResponseNotAllowed(['GET', 'POST'])
        cargo = _cargo_for_edit(cargo_dashboard, tracking_id)
        deadline_value = request.POST.get('deadline', '')

        if request.method == 'POST':
            try:
                deadline = date.fromisoformat(deadline_value)
            except ValueError:
                context = _deadline_context(
                    cargo,
                    deadline_value,
                    'Enter a valid arrival deadline.',
                )
                return _render_dialog(request, _DIALOG_TEMPLATES['deadline'], context)
            try:
                cargo_specification.change_deadline(
                    cargo.tracking_id,
                    timezone.make_aware(datetime.combine(deadline, time.min)),
                )
            except LookupError as error:
                raise Http404(str(error)) from error
            return _refreshed_table(request, cargo_dashboard)

        return _render_dialog(
            request,
            _DIALOG_TEMPLATES['deadline'],
            _deadline_context(cargo),
        )

    return destination_dialog, deadline_dialog
