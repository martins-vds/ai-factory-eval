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


def create_booking_dialog_views(
    cargo_dashboard: CargoDashboard,
    cargo_specification: CargoSpecification,
    list_shipping_locations: Callable[[], list[Location]],
) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
    def find_cargo(tracking_id: str) -> Cargo:
        cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
        if cargo is None:
            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
        return cargo

    def refreshed_table(request: HttpRequest) -> HttpResponse:
        cargos = cargo_dashboard.get_dashboard()
        response = render(
            request,
            'booking/dashboard/not_routed_table.html',
            {'not_routed_cargos': cargos.not_routed_cargos},
        )
        response['HX-Retarget'] = '#not-routed-cargo'
        response['HX-Reswap'] = 'outerHTML'
        return response

    def update_response(request: HttpRequest) -> HttpResponse:
        if request.headers.get('HX-Request') == 'true':
            return refreshed_table(request)
        return redirect('/admin/dashboard/')

    def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        if request.method not in {'GET', 'POST'}:
            return HttpResponseNotAllowed(['GET', 'POST'])

        cargo = find_cargo(tracking_id)
        specification = cargo.route_specification
        destinations = [
            location
            for location in list_shipping_locations()
            if location not in {specification.origin, specification.destination}
        ]
        context = {'cargo': cargo, 'destinations': destinations}

        if request.method == 'POST':
            selected_code = request.POST.get('destination')
            destination = next(
                (location for location in destinations if location.unlocode.value == selected_code),
                None,
            )
            if destination is None:
                context['destination_error'] = 'Select a valid destination.'
            else:
                try:
                    cargo_specification.change_destination(cargo.tracking_id, destination)
                except LookupError as error:
                    raise Http404(str(error)) from error
                return update_response(request)

        return render(
            request,
            'booking/dialogs/destination.html',
            context,
        )

    def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
        if request.method not in {'GET', 'POST'}:
            return HttpResponseNotAllowed(['GET', 'POST'])

        cargo = find_cargo(tracking_id)
        deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
        context = {'cargo': cargo, 'deadline_value': deadline_value}

        if request.method == 'POST':
            deadline_value = request.POST.get('deadline', '')
            try:
                deadline = date.fromisoformat(deadline_value)
            except ValueError:
                context['deadline_error'] = 'Enter a valid arrival deadline.'
            else:
                try:
                    cargo_specification.change_deadline(
                        cargo.tracking_id,
                        timezone.make_aware(datetime.combine(deadline, time.min)),
                    )
                except LookupError as error:
                    raise Http404(str(error)) from error
                return update_response(request)
            context['deadline_value'] = deadline_value

        return render(
            request,
            'booking/dialogs/deadline.html',
            context,
        )

    return destination_dialog, deadline_dialog
