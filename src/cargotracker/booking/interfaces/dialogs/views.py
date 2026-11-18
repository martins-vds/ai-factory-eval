from collections.abc import Callable
from datetime import date, datetime, time

from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render
from django.utils import timezone

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.location import Location


def _refreshed_not_routed_table(
    request: HttpRequest, cargo_dashboard: CargoDashboard
) -> HttpResponse:
    dashboard = cargo_dashboard.get_dashboard()
    response = render(
        request,
        'booking/dashboard/not_routed_table.html',
        {'not_routed_cargos': dashboard.not_routed_cargos, 'out_of_band': True},
    )
    response['HX-Reswap'] = 'none'
    return response


def create_booking_dialog_views(
    cargo_dashboard: CargoDashboard,
    cargo_specification: CargoSpecification,
    list_shipping_locations: Callable[[], list[Location]],
) -> tuple[
    Callable[[HttpRequest, str], HttpResponse],
    Callable[[HttpRequest, str], HttpResponse],
]:
    def change_destination(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
        if cargo is None:
            return render(request, 'booking/dialogs/not_found.html', status=404)

        origin = cargo.route_specification.origin
        destination = cargo.route_specification.destination
        available_locations = list_shipping_locations()
        locations = [
            location
            for location in available_locations
            if location != origin and location != destination
        ]
        if request.method == 'GET':
            return render(
                request,
                'booking/dialogs/destination.html',
                {'cargo': cargo, 'destinations': locations},
            )
        if request.method != 'POST':
            return HttpResponseNotAllowed(['GET', 'POST'])

        destination_value = request.POST.get('destination', '')
        selected_destination = next(
            (
                location
                for location in available_locations
                if location.unlocode.value == destination_value
            ),
            None,
        )
        if selected_destination is None:
            return render(
                request,
                'booking/dialogs/destination.html',
                {
                    'cargo': cargo,
                    'destinations': locations,
                    'destination_value': destination_value,
                    'destination_error': 'Select a valid destination.',
                },
            )

        cargo_specification.change_destination(TrackingId(tracking_id), selected_destination)
        return _refreshed_not_routed_table(request, cargo_dashboard)

    def change_deadline(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
        if cargo is None:
            return render(request, 'booking/dialogs/not_found.html', status=404)
        if request.method == 'GET':
            return render(request, 'booking/dialogs/deadline.html', {'cargo': cargo})
        if request.method != 'POST':
            return HttpResponseNotAllowed(['GET', 'POST'])

        deadline_value = request.POST.get('deadline', '')
        try:
            deadline = date.fromisoformat(deadline_value)
        except ValueError:
            return render(
                request,
                'booking/dialogs/deadline.html',
                {
                    'cargo': cargo,
                    'deadline_value': deadline_value,
                    'deadline_error': 'Enter a valid arrival deadline.',
                },
            )

        cargo_specification.change_deadline(
            TrackingId(tracking_id),
            timezone.make_aware(datetime.combine(deadline, time.min)),
        )
        return _refreshed_not_routed_table(request, cargo_dashboard)

    return change_destination, change_deadline
