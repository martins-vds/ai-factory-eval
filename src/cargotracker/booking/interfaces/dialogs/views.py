from collections.abc import Callable
from datetime import date, datetime, time

from django.http import Http404, HttpRequest, HttpResponse, HttpResponseNotAllowed
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


def _render_dialog(
    request: HttpRequest,
    dialog: str,
    context: dict[str, object],
    status: int = 200,
) -> HttpResponse:
    template = (
        f'booking/dialogs/_{dialog}_form.html'
        if request.headers.get('HX-Request') == 'true'
        else f'booking/dialogs/{dialog}.html'
    )
    return render(request, template, context, status=status)


def _complete_dialog(request: HttpRequest) -> HttpResponse:
    if request.headers.get('HX-Request') == 'true':
        response = HttpResponse()
        response['HX-Redirect'] = '/admin/dashboard/'
        return response
    return redirect('/admin/dashboard/')


def create_booking_dialog_views(
    cargo_dashboard: CargoDashboard,
    cargo_specification: CargoSpecification,
    list_shipping_locations: Callable[[], list[Location]],
) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
    def destination(request: HttpRequest, tracking_id: str) -> HttpResponse:
        if request.method not in {'GET', 'POST'}:
            return HttpResponseNotAllowed(['GET', 'POST'])
        cargo = _find_cargo(cargo_dashboard, tracking_id)
        route_specification = cargo.route_specification
        locations = [
            location
            for location in list_shipping_locations()
            if location.unlocode
            not in {
                route_specification.origin.unlocode,
                route_specification.destination.unlocode,
            }
        ]
        context: dict[str, object] = {
            'cargo': cargo,
            'locations': locations,
        }

        if request.method == 'POST':
            if request.POST.get('action') == 'cancel':
                return _complete_dialog(request)
            destination_code = request.POST.get('destination')
            selected_destination = next(
                (location for location in locations if location.unlocode.value == destination_code),
                None,
            )
            if selected_destination is None:
                context['destination_error'] = 'Select a valid destination.'
                return _render_dialog(request, 'destination', context)
            cargo_specification.change_destination(
                TrackingId(tracking_id),
                selected_destination,
            )
            return _complete_dialog(request)

        return _render_dialog(request, 'destination', context)

    def deadline(request: HttpRequest, tracking_id: str) -> HttpResponse:
        if request.method not in {'GET', 'POST'}:
            return HttpResponseNotAllowed(['GET', 'POST'])
        cargo = _find_cargo(cargo_dashboard, tracking_id)
        deadline_value = cargo.route_specification.arrival_deadline.strftime('%Y-%m-%d')
        context: dict[str, object] = {
            'cargo': cargo,
            'deadline_value': deadline_value,
        }

        if request.method == 'POST':
            if request.POST.get('action') == 'cancel':
                return _complete_dialog(request)
            deadline_value = request.POST.get('deadline') or ''
            context['deadline_value'] = deadline_value
            try:
                arrival_date = date.fromisoformat(deadline_value)
            except ValueError:
                context['deadline_error'] = 'Enter a valid arrival deadline.'
                return _render_dialog(request, 'deadline', context)
            cargo_specification.change_deadline(
                TrackingId(tracking_id),
                timezone.make_aware(datetime.combine(arrival_date, time.min)),
            )
            return _complete_dialog(request)

        return _render_dialog(request, 'deadline', context)

    return destination, deadline
