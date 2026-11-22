from collections.abc import Callable
from datetime import date, datetime, time

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location


def _render_dialog(
    request: HttpRequest,
    template: str,
    context: dict[str, object],
    status: int = 200,
) -> HttpResponse:
    if request.headers.get('HX-Request') == 'true':
        return render(request, template, {**context, 'is_dialog': True}, status=status)
    page_context = {**context, 'dialog_template': template}
    if cargo := context.get('cargo'):
        page_context['tracking_id'] = cargo.tracking_id.value
    return render(
        request,
        'booking/dialogs/page.html',
        page_context,
        status=status,
    )


def _not_found(request: HttpRequest, tracking_id: str) -> HttpResponse:
    return _render_dialog(
        request,
        'booking/dialogs/not_found.html',
        {'tracking_id': tracking_id},
        404,
    )


def _dialog_complete(request: HttpRequest) -> HttpResponse:
    if request.headers.get('HX-Request') == 'true':
        return HttpResponse(status=204, headers={'HX-Redirect': '/admin/dashboard/'})
    return redirect('/admin/dashboard/')


def create_destination_dialog_view(
    cargo_dashboard: CargoDashboard,
    specification: CargoSpecification,
    list_shipping_locations: Callable[[], list[Location]],
) -> Callable[[HttpRequest, str], HttpResponse]:
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
        if cargo is None:
            return _not_found(request, tracking_id)
        choices = [
            location
            for location in list_shipping_locations()
            if location
            not in (cargo.route_specification.origin, cargo.route_specification.destination)
        ]
        if request.method == 'POST':
            destination = next(
                (
                    location
                    for location in choices
                    if location.unlocode.value == request.POST.get('destination')
                ),
                None,
            )
            if destination is None:
                return _render_dialog(
                    request,
                    'booking/dialogs/destination.html',
                    {
                        'cargo': cargo,
                        'destination_choices': choices,
                        'error': 'Select a valid destination.',
                    },
                    400,
                )
            specification.change_destination(TrackingId(tracking_id), destination)
            return _dialog_complete(request)
        return _render_dialog(
            request,
            'booking/dialogs/destination.html',
            {'cargo': cargo, 'destination_choices': choices},
        )

    return destination_dialog


def create_deadline_dialog_view(
    cargo_dashboard: CargoDashboard,
    specification: CargoSpecification,
) -> Callable[[HttpRequest, str], HttpResponse]:
    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
        if cargo is None:
            return _not_found(request, tracking_id)
        deadline_value = cargo.route_specification.arrival_deadline.strftime('%Y-%m-%d')
        if request.method == 'POST':
            deadline_value = request.POST.get('deadline', '')
            try:
                deadline = date.fromisoformat(deadline_value)
            except ValueError:
                return _render_dialog(
                    request,
                    'booking/dialogs/deadline.html',
                    {
                        'cargo': cargo,
                        'deadline_value': deadline_value,
                        'error': 'Enter a valid arrival deadline.',
                    },
                    400,
                )
            specification.change_deadline(
                TrackingId(tracking_id),
                timezone.make_aware(datetime.combine(deadline, time.min)),
            )
            return _dialog_complete(request)
        return _render_dialog(
            request,
            'booking/dialogs/deadline.html',
            {'cargo': cargo, 'deadline_value': deadline_value},
        )

    return deadline_dialog
