from collections.abc import Callable
from datetime import UTC, date, datetime, time

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.cargo.domain.repository import CargoRepository
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.domain.repository import LocationRepository


def create_booking_dialog_views(
    cargo_repository: CargoRepository,
    location_repository: LocationRepository,
    specification: CargoSpecification,
) -> tuple[
    Callable[[HttpRequest, str], HttpResponse],
    Callable[[HttpRequest, str], HttpResponse],
]:
    @require_http_methods(['GET', 'POST'])
    def change_destination(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo_tracking_id = TrackingId(tracking_id)
        cargo = cargo_repository.find(cargo_tracking_id)
        if cargo is None:
            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')

        destinations = [
            location
            for location in location_repository.find_all()
            if location
            not in (cargo.route_specification.origin, cargo.route_specification.destination)
        ]
        error = ''
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
                error = 'Select a valid destination.'
            else:
                try:
                    specification.change_destination(cargo_tracking_id, destination)
                except LookupError as exc:
                    raise Http404(str(exc)) from exc
                return _refresh_response()

        return render(
            request,
            'booking/dialogs/destination.html',
            {
                'cargo': cargo,
                'destinations': destinations,
                'error': error,
                'form_url': request.path,
            },
        )

    @require_http_methods(['GET', 'POST'])
    def change_deadline(request: HttpRequest, tracking_id: str) -> HttpResponse:
        cargo_tracking_id = TrackingId(tracking_id)
        cargo = cargo_repository.find(cargo_tracking_id)
        if cargo is None:
            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')

        deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
        error = ''
        if request.method == 'POST':
            deadline_value = request.POST.get('arrival_deadline', '')
            try:
                deadline = datetime.combine(
                    date.fromisoformat(deadline_value),
                    time.min,
                    tzinfo=UTC,
                )
            except ValueError:
                error = 'Enter a valid arrival deadline.'
            else:
                try:
                    specification.change_deadline(cargo_tracking_id, deadline)
                except LookupError as exc:
                    raise Http404(str(exc)) from exc
                return _refresh_response()

        return render(
            request,
            'booking/dialogs/deadline.html',
            {
                'cargo': cargo,
                'deadline_value': deadline_value,
                'error': error,
                'form_url': request.path,
            },
        )

    return change_destination, change_deadline


def _refresh_response() -> HttpResponse:
    response = HttpResponse(status=204)
    response['HX-Refresh'] = 'true'
    return response
