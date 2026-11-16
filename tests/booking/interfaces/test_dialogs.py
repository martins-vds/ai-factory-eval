import re
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from django.core.management import call_command
from django.http import Http404
from django.template.loader import render_to_string
from django.test import RequestFactory

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.booking.interfaces.dialogs.views import create_booking_dialog_views
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository


@pytest.fixture
def booking_dialogs():
    call_command('seed_sample_data')
    cargo_repository = DjangoCargoRepository()
    location_repository = DjangoLocationRepository()
    return (
        create_booking_dialog_views(
            CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
            CargoDashboard(cargo_repository),
            location_repository.find_all,
        ),
        cargo_repository,
        location_repository,
    )


def _request(factory, method, path, data=None):
    request = getattr(factory, method)(path, data or {})
    request.user = SimpleNamespace(is_authenticated=False)
    return request


@pytest.mark.django_db
def test_not_routed_table_opens_destination_and_deadline_dialogs():
    call_command('seed_sample_data')
    cargo = DjangoCargoRepository().find(TrackingId('DEF789'))
    assert cargo is not None

    content = render_to_string(
        'booking/dashboard/not_routed_table.html',
        {'not_routed_cargos': [cargo]},
    )

    assert 'Edit destination' in content
    assert 'Edit deadline' in content
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in content
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in content
    assert 'showModal()' in content
    assert 'href="/admin/cargo/DEF789/route/"' in content


@pytest.mark.django_db
def test_destination_dialog_shows_current_values_and_filters_options_without_mutation(
    booking_dialogs,
):
    (change_destination, _), cargo_repository, location_repository = booking_dialogs
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    location_codes = [location.unlocode.value for location in location_repository.find_all()]

    response = change_destination(
        _request(RequestFactory(), 'get', '/admin/cargo/DEF789/destination/'),
        'DEF789',
    )
    content = response.content.decode()
    options = re.search(r'<select\b[^>]*>(.*?)</select>', content, re.DOTALL)
    assert options is not None

    assert response.status_code == 200
    assert cargo.route_specification.origin.name in content
    assert cargo.route_specification.destination.name in content
    assert cargo.route_specification.origin.unlocode.value not in options.group(1)
    assert cargo.route_specification.destination.unlocode.value not in options.group(1)
    remaining_location = next(
        location
        for location in location_repository.find_all()
        if location not in (cargo.route_specification.origin, cargo.route_specification.destination)
    )
    assert f'value="{remaining_location.unlocode.value}"' in options.group(1)
    assert 'destination-error' not in content

    subsequent = change_destination(
        _request(RequestFactory(), 'get', '/admin/cargo/DEF789/destination/'),
        'DEF789',
    )
    subsequent_options = re.search(
        r'<select\b[^>]*>(.*?)</select>', subsequent.content.decode(), re.DOTALL
    )
    assert subsequent_options is not None
    assert subsequent_options.group(1) == options.group(1)
    assert [
        location.unlocode.value for location in location_repository.find_all()
    ] == location_codes


@pytest.mark.parametrize(
    ('deadline_data', 'retained_value'),
    [({}, ''), ({'deadline': 'not-a-date'}, 'not-a-date')],
    ids=('missing', 'malformed'),
)
@pytest.mark.django_db
def test_invalid_deadline_shows_field_error_and_keeps_dialog_open(
    booking_dialogs, deadline_data, retained_value
):
    (_, change_deadline), cargo_repository, _ = booking_dialogs
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    previous_deadline = cargo.route_specification.arrival_deadline

    response = change_deadline(
        _request(
            RequestFactory(),
            'post',
            '/admin/cargo/DEF789/deadline/',
            deadline_data,
        ),
        'DEF789',
    )
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Enter a valid date.' in content
    assert 'role="alert"' in content
    assert 'aria-invalid="true"' in content
    assert f'value="{retained_value}"' in content
    assert cargo_repository.find(TrackingId('DEF789')).route_specification.arrival_deadline == (
        previous_deadline
    )
    assert 'HX-Trigger' not in response


@pytest.mark.django_db
def test_invalid_destination_shows_field_error_without_updating_cargo(booking_dialogs):
    (change_destination, _), cargo_repository, _ = booking_dialogs
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    previous_specification = cargo.route_specification

    response = change_destination(
        _request(
            RequestFactory(),
            'post',
            '/admin/cargo/DEF789/destination/',
            {'destination': cargo.route_specification.origin.unlocode.value},
        ),
        'DEF789',
    )
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Select a valid destination.' in content
    assert 'role="alert"' in content
    assert cargo_repository.find(TrackingId('DEF789')).route_specification == (
        previous_specification
    )


@pytest.mark.django_db
def test_dialog_views_cover_initial_values_and_all_update_paths(booking_dialogs):
    (change_destination, change_deadline), cargo_repository, location_repository = booking_dialogs
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    origin = cargo.route_specification.origin
    previous_destination = cargo.route_specification.destination
    previous_deadline = cargo.route_specification.arrival_deadline
    other_destination = next(
        location
        for location in location_repository.find_all()
        if location not in (origin, previous_destination)
    )

    destination_form = change_destination(
        _request(RequestFactory(), 'get', '/admin/cargo/DEF789/destination/'),
        'DEF789',
    )
    destination_content = destination_form.content.decode()
    assert origin.name in destination_content
    assert previous_destination.name in destination_content
    assert other_destination.unlocode.value in destination_content
    assert 'destination-error' not in destination_content

    invalid_destination = change_destination(
        _request(
            RequestFactory(),
            'post',
            '/admin/cargo/DEF789/destination/',
            {'destination': origin.unlocode.value},
        ),
        'DEF789',
    )
    assert 'Select a valid destination.' in invalid_destination.content.decode()

    updated_destination = change_destination(
        _request(
            RequestFactory(),
            'post',
            '/admin/cargo/DEF789/destination/',
            {'destination': other_destination.unlocode.value},
        ),
        'DEF789',
    )
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo.route_specification.origin == origin
    assert cargo.route_specification.destination == other_destination
    assert cargo.route_specification.arrival_deadline == previous_deadline
    assert 'id="not-routed-cargo"' in updated_destination.content.decode()
    assert updated_destination['HX-Retarget'] == '#not-routed-cargo'
    assert updated_destination['HX-Reswap'] == 'outerHTML'
    assert updated_destination['HX-Trigger'] == 'booking-dialog-complete'

    deadline_form = change_deadline(
        _request(RequestFactory(), 'get', '/admin/cargo/DEF789/deadline/'),
        'DEF789',
    )
    deadline_content = deadline_form.content.decode()
    assert f'value="{previous_deadline.date().isoformat()}"' in deadline_content
    assert origin.name in deadline_content
    assert other_destination.name in deadline_content
    assert 'deadline-error' not in deadline_content

    invalid_deadline = change_deadline(
        _request(
            RequestFactory(),
            'post',
            '/admin/cargo/DEF789/deadline/',
            {'deadline': 'not-a-date'},
        ),
        'DEF789',
    )
    assert 'Enter a valid date.' in invalid_deadline.content.decode()

    updated_deadline = change_deadline(
        _request(
            RequestFactory(),
            'post',
            '/admin/cargo/DEF789/deadline/',
            {'deadline': '2027-01-15'},
        ),
        'DEF789',
    )
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo.route_specification.origin == origin
    assert cargo.route_specification.destination == other_destination
    assert cargo.route_specification.arrival_deadline == datetime(2027, 1, 15, tzinfo=UTC)
    assert 'id="not-routed-cargo"' in updated_deadline.content.decode()
    assert updated_deadline['HX-Retarget'] == '#not-routed-cargo'
    assert updated_deadline['HX-Reswap'] == 'outerHTML'
    assert updated_deadline['HX-Trigger'] == 'booking-dialog-complete'

    for dialog, path in (
        (change_destination, '/admin/cargo/DEF789/destination/'),
        (change_deadline, '/admin/cargo/DEF789/deadline/'),
    ):
        response = dialog(_request(RequestFactory(), 'put', path), 'DEF789')
        assert response.status_code == 405
        assert response['Allow'] == 'GET, POST'

    with pytest.raises(Http404, match='Cargo with tracking ID MISSING not found.'):
        change_destination(
            _request(RequestFactory(), 'get', '/admin/cargo/MISSING/destination/'),
            'MISSING',
        )


@pytest.mark.django_db
def test_destination_dialog_updates_cargo_and_returns_refreshed_table_without_warning(
    booking_dialogs,
):
    (change_destination, _), cargo_repository, location_repository = booking_dialogs
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    other_destination = next(
        location
        for location in location_repository.find_all()
        if location not in (cargo.route_specification.origin, cargo.route_specification.destination)
    )
    deadline = cargo.route_specification.arrival_deadline
    origin = cargo.route_specification.origin

    response = change_destination(
        _request(
            RequestFactory(),
            'post',
            '/admin/cargo/DEF789/destination/',
            {'destination': other_destination.unlocode.value},
        ),
        'DEF789',
    )
    updated = cargo_repository.find(TrackingId('DEF789'))
    content = response.content.decode()

    assert response.status_code == 200
    assert updated.route_specification.origin == origin
    assert updated.route_specification.destination == other_destination
    assert updated.route_specification.arrival_deadline == deadline
    assert 'id="not-routed-cargo"' in content
    assert other_destination.name in content
    assert response['HX-Trigger'] == 'booking-dialog-complete'
    assert response['HX-Retarget'] == '#not-routed-cargo'
    assert response['HX-Reswap'] == 'outerHTML'
    assert 'Widget for var' not in content


@pytest.mark.django_db
def test_deadline_dialog_updates_cargo_and_returns_refreshed_table_without_warning(
    booking_dialogs,
):
    (_, change_deadline), cargo_repository, _ = booking_dialogs
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    origin = cargo.route_specification.origin
    destination = cargo.route_specification.destination

    response = change_deadline(
        _request(
            RequestFactory(),
            'post',
            '/admin/cargo/DEF789/deadline/',
            {'deadline': '2027-01-15'},
        ),
        'DEF789',
    )
    updated = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 200
    assert updated.route_specification.arrival_deadline == datetime(2027, 1, 15, tzinfo=UTC)
    assert updated.route_specification.origin == origin
    assert updated.route_specification.destination == destination
    assert 'id="not-routed-cargo"' in response.content.decode()
    assert response['HX-Trigger'] == 'booking-dialog-complete'
    assert response['HX-Retarget'] == '#not-routed-cargo'
    assert response['HX-Reswap'] == 'outerHTML'
    assert 'Widget for var' not in response.content.decode()


@pytest.mark.parametrize(
    ('dialog_index', 'path'),
    [
        (0, '/admin/cargo/DEF789/destination/'),
        (1, '/admin/cargo/DEF789/deadline/'),
    ],
)
@pytest.mark.django_db
def test_dialogs_reject_unsupported_methods_with_allowed_methods_header(
    booking_dialogs, dialog_index, path
):
    dialogs, _, _ = booking_dialogs

    response = dialogs[dialog_index](
        _request(RequestFactory(), 'put', path),
        'DEF789',
    )

    assert response.status_code == 405
    assert response['Allow'] == 'GET, POST'


@pytest.mark.django_db
def test_dialogs_return_not_found_for_unknown_cargo(booking_dialogs):
    (change_destination, _), _, _ = booking_dialogs

    with pytest.raises(Http404, match='Cargo with tracking ID MISSING not found.'):
        change_destination(
            _request(RequestFactory(), 'get', '/admin/cargo/MISSING/destination/'),
            'MISSING',
        )
