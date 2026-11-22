from collections.abc import Callable
from datetime import date, datetime, time

from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.utils import timezone

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location


def _cargo_or_error(request: HttpRequest, cargo_dashboard: CargoDashboard, tracking_id: str):
    cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
    if cargo is None:
        return None, render(
            request,
            'booking/dialogs/not_found.html',
            {'tracking_id': tracking_id},
            status=404,
        )
    return cargo, None


def _updated_response(request: HttpRequest) -> HttpResponse:
    if request.headers.get('HX-Request') == 'true':
        return HttpResponse(status=204, headers={'HX-Redirect': '/admin/dashboard/'})
    return redirect('/admin/dashboard/')


def create_booking_dialog_views(
    specification: CargoSpecification,
    cargo_dashboard: CargoDashboard,
    list_shipping_locations: Callable[[], list[Location]],
) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        if request.method not in {'GET', 'POST'}:
            return HttpResponseNotAllowed(['GET', 'POST'])

        cargo, error_response = _cargo_or_error(request, cargo_dashboard, tracking_id)
        if error_response is not None:
            return error_response

        locations = list_shipping_locations()
        origin = cargo.route_specification.origin
        current_destination = cargo.route_specification.destination
        destinations = [
            location
            for location in locations
            if location != origin and location != current_destination
        ]
        context = {
            'cargo': cargo,
            'destinations': destinations,
        }

        if request.method == 'POST':
            destination = next(
                (
                    location
                    for location in destinations
                    if location.unlocode.value == request.POST.get('destination')
                ),
                None,
            )
            if destination is None:
                context['destination_error'] = 'Select a valid destination.'
                return render(request, 'booking/dialogs/destination.html', context, status=400)
            specification.change_destination(TrackingId(tracking_id), destination)
            return _updated_response(request)

        return render(request, 'booking/dialogs/destination.html', context)

    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        if request.method not in {'GET', 'POST'}:
            return HttpResponseNotAllowed(['GET', 'POST'])

        cargo, error_response = _cargo_or_error(request, cargo_dashboard, tracking_id)
        if error_response is not None:
            return error_response

        deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
        context = {'cargo': cargo, 'deadline_value': deadline_value}

        if request.method == 'POST':
            deadline_value = request.POST.get('deadline', '')
            context['deadline_value'] = deadline_value
            try:
                deadline = datetime.combine(date.fromisoformat(deadline_value), time.min)
            except ValueError:
                context['deadline_error'] = 'Enter a valid arrival deadline.'
                return render(request, 'booking/dialogs/deadline.html', context, status=400)
            specification.change_deadline(
                TrackingId(tracking_id),
                timezone.make_aware(deadline),
            )
            return _updated_response(request)

        return render(request, 'booking/dialogs/deadline.html', context)

    return destination_dialog, deadline_dialog
