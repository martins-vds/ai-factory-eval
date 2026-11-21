import re
from datetime import date, datetime, time

import pytest
from django.core.management import call_command
from django.template.loader import render_to_string
from django.test import RequestFactory
from django.utils import timezone

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.booking.interfaces.dialogs.views import create_dialog_views
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository


def _dialog_views():
    cargo_repository = DjangoCargoRepository()
    locations = DjangoLocationRepository().find_all()
    return (
        create_dialog_views(
            CargoDashboard(cargo_repository),
            CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
            lambda: locations,
        ),
        cargo_repository,
        locations,
    )


def _not_routed_table(cargo_repository):
    dashboard = CargoDashboard(cargo_repository)
    return render_to_string(
        'booking/dashboard/not_routed_table.html',
        {'not_routed_cargos': dashboard.get_dashboard().not_routed_cargos},
        request=RequestFactory().get('/admin/dashboard/'),
    )


@pytest.mark.django_db
def test_not_routed_table_opens_destination_and_deadline_editors():
    call_command('seed_sample_data')
    (destination_dialog, _), cargo_repository, _ = _dialog_views()

    content = _not_routed_table(cargo_repository)

    assert 'href="/admin/cargo/DEF789/route/"' in content
    assert 'hx-get="/admin/cargo/DEF789/destination-dialog/"' in content
    assert 'hx-get="/admin/cargo/DEF789/deadline-dialog/"' in content
    assert 'id="cargo-dialog"' in content
    assert 'hx-on::before-swap' in content
    assert destination_dialog is not None


@pytest.mark.django_db
def test_destination_dialog_shows_values_and_repeated_filtered_options():
    call_command('seed_sample_data')
    (destination_dialog, _), cargo_repository, locations = _dialog_views()
    original_locations = list(locations)
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None

    request = RequestFactory().get('/admin/cargo/DEF789/destination-dialog/')
    first = destination_dialog(request, 'DEF789')
    second = destination_dialog(request, 'DEF789')
    first_content = first.content.decode()
    second_content = second.content.decode()
    first_options = re.search(r'<select\b[^>]*>(.*?)</select>', first_content, re.DOTALL)
    second_options = re.search(r'<select\b[^>]*>(.*?)</select>', second_content, re.DOTALL)

    assert first.status_code == 200
    assert cargo.route_specification.origin.name in first_content
    assert cargo.route_specification.destination.name in first_content
    assert first_options is not None
    assert second_options is not None
    assert first_options.group(1) == second_options.group(1)
    assert f'value="{cargo.route_specification.origin.unlocode.value}"' not in first_options.group(
        1
    )
    assert (
        f'value="{cargo.route_specification.destination.unlocode.value}"'
        not in first_options.group(1)
    )
    assert locations == original_locations


@pytest.mark.django_db
def test_deadline_dialog_prefills_the_current_deadline():
    call_command('seed_sample_data')
    (_, deadline_dialog), cargo_repository, _ = _dialog_views()
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None

    response = deadline_dialog(
        RequestFactory().get('/admin/cargo/DEF789/deadline-dialog/'),
        'DEF789',
    )

    assert response.status_code == 200
    assert cargo.route_specification.origin.name in response.content.decode()
    assert cargo.route_specification.destination.name in response.content.decode()
    assert (
        f'value="{cargo.route_specification.arrival_deadline.date().isoformat()}"'
        in response.content.decode()
    )


@pytest.mark.django_db
def test_deadline_parse_error_is_shown_without_changing_the_cargo():
    call_command('seed_sample_data')
    (_, deadline_dialog), cargo_repository, _ = _dialog_views()
    cargo_before = cargo_repository.find(TrackingId('DEF789'))
    assert cargo_before is not None

    response = deadline_dialog(
        RequestFactory().post(
            '/admin/cargo/DEF789/deadline-dialog/',
            {'deadline': 'not-a-date'},
        ),
        'DEF789',
    )
    cargo_after = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 200
    assert 'Enter a valid arrival deadline.' in response.content.decode()
    assert cargo_after is not None
    assert (
        cargo_after.route_specification.arrival_deadline
        == cargo_before.route_specification.arrival_deadline
    )


@pytest.mark.django_db
def test_destination_update_preserves_other_fields_and_refreshes_the_table():
    call_command('seed_sample_data')
    (destination_dialog, _), cargo_repository, locations = _dialog_views()
    cargo_before = cargo_repository.find(TrackingId('DEF789'))
    assert cargo_before is not None
    destination = next(
        location
        for location in locations
        if location
        not in (
            cargo_before.route_specification.origin,
            cargo_before.route_specification.destination,
        )
    )

    response = destination_dialog(
        RequestFactory().post(
            '/admin/cargo/DEF789/destination-dialog/',
            {'destination': destination.unlocode.value},
        ),
        'DEF789',
    )
    cargo_after = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 204
    assert response.headers['HX-Redirect'] == '/admin/dashboard/'
    assert cargo_after is not None
    assert cargo_after.route_specification.origin == cargo_before.route_specification.origin
    assert cargo_after.route_specification.destination == destination
    assert (
        cargo_after.route_specification.arrival_deadline
        == cargo_before.route_specification.arrival_deadline
    )
    assert destination.name in _not_routed_table(cargo_repository)


@pytest.mark.django_db
def test_deadline_update_preserves_route_fields_and_refreshes_the_table():
    call_command('seed_sample_data')
    (_, deadline_dialog), cargo_repository, _ = _dialog_views()
    cargo_before = cargo_repository.find(TrackingId('DEF789'))
    assert cargo_before is not None
    new_deadline = date(2027, 1, 15)

    response = deadline_dialog(
        RequestFactory().post(
            '/admin/cargo/DEF789/deadline-dialog/',
            {'deadline': new_deadline.isoformat()},
        ),
        'DEF789',
    )
    cargo_after = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 204
    assert response.headers['HX-Redirect'] == '/admin/dashboard/'
    assert cargo_after is not None
    assert cargo_after.route_specification.origin == cargo_before.route_specification.origin
    assert cargo_after.route_specification.destination == cargo_before.route_specification.destination
    assert cargo_after.route_specification.arrival_deadline == timezone.make_aware(
        datetime.combine(new_deadline, time.min)
    )
    assert new_deadline.strftime('%m/%d/%Y') in _not_routed_table(cargo_repository)
