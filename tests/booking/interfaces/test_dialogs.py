import re
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from django.core.management import call_command
from django.test import RequestFactory, override_settings
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.booking.interfaces.dialogs.views import create_dialog_views
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository

cargo_repository = DjangoCargoRepository()
dashboard_view, _ = create_booking_views(CargoDashboard(cargo_repository))
destination_dialog_view, deadline_dialog_view = create_dialog_views(
    CargoDashboard(cargo_repository),
    CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
    DjangoLocationRepository().find_all,
)
urlpatterns = [
    path('admin/dashboard/', dashboard_view),
    path('admin/cargo/<str:tracking_id>/destination/', destination_dialog_view),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_dialog_view),
]


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_not_routed_table_opens_destination_and_deadline_dialogs(client):
    call_command('seed_sample_data')

    response = client.get('/admin/dashboard/')
    content = response.content.decode()
    not_routed_table = content.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]

    assert response.status_code == 200
    assert 'data-tracking-id="DEF789"' in not_routed_table
    assert 'href="/admin/cargo/DEF789/route/"' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in not_routed_table
    assert 'id="cargo-edit-dialog"' in not_routed_table


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_dialogs_render_the_cargo_destination_and_deadline(client):
    call_command('seed_sample_data')
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None

    destination_response = client.get('/admin/cargo/DEF789/destination/')
    deadline_response = client.get('/admin/cargo/DEF789/deadline/')

    assert destination_response.status_code == 200
    assert 'Hong Kong' in destination_response.content.decode()
    assert 'Melbourne' in destination_response.content.decode()
    assert deadline_response.status_code == 200
    assert (
        f'value="{cargo.route_specification.arrival_deadline.date().isoformat()}"'
        in deadline_response.content.decode()
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_filters_options_without_mutating_backing_locations():
    call_command('seed_sample_data')
    locations = DjangoLocationRepository().find_all()
    original_locations = locations.copy()
    dialog_view, _ = create_dialog_views(
        CargoDashboard(cargo_repository),
        CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
        lambda: locations,
    )

    request = RequestFactory().get('/')
    request.user = SimpleNamespace(is_authenticated=False)
    response = dialog_view(request, 'DEF789')
    first_content = response.content.decode()
    repeated_request = RequestFactory().get('/')
    repeated_request.user = SimpleNamespace(is_authenticated=False)
    repeated_content = dialog_view(repeated_request, 'DEF789').content.decode()
    options = re.search(r'<select\b[^>]*>(.*?)</select>', first_content, re.DOTALL)
    repeated_options = re.search(r'<select\b[^>]*>(.*?)</select>', repeated_content, re.DOTALL)
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    assert options is not None
    assert repeated_options is not None
    option_values = re.findall(r'<option\b[^>]*value="([^"]+)"', options.group(1))

    assert response.status_code == 200
    assert cargo.route_specification.origin.unlocode.value not in option_values
    assert cargo.route_specification.destination.unlocode.value not in option_values
    assert options.group(1) == repeated_options.group(1)
    assert locations == original_locations


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_unknown_cargo_dialog_returns_a_rendered_not_found_response(client):
    response = client.get('/admin/cargo/MISSING1/destination/', HTTP_HX_REQUEST='true')

    assert response.status_code == 404
    assert 'MISSING1' in response.content.decode()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_shows_a_field_error_for_unparseable_input(client):
    call_command('seed_sample_data')
    original = cargo_repository.find(TrackingId('DEF789'))
    assert original is not None

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': 'not-a-date'},
        HTTP_HX_REQUEST='true',
    )
    updated = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 400
    assert 'Enter a valid arrival deadline.' in response.content.decode()
    assert updated is not None
    assert (
        updated.route_specification.arrival_deadline
        == original.route_specification.arrival_deadline
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_shows_an_error_for_an_unavailable_destination(client):
    call_command('seed_sample_data')
    original = cargo_repository.find(TrackingId('DEF789'))
    assert original is not None

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'UNKNOWN'},
        HTTP_HX_REQUEST='true',
    )
    updated = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 400
    assert 'Select a valid destination.' in response.content.decode()
    assert updated is not None
    assert updated.route_specification.destination == original.route_specification.destination


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_update_preserves_other_route_specification_fields(client):
    call_command('seed_sample_data')
    original = cargo_repository.find(TrackingId('DEF789'))
    assert original is not None
    destination = next(
        location
        for location in DjangoLocationRepository().find_all()
        if location
        not in (original.route_specification.origin, original.route_specification.destination)
    )

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': destination.unlocode.value},
        HTTP_HX_REQUEST='true',
    )
    updated = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 204
    assert response.headers['HX-Trigger'] == 'cargoUpdated'
    assert updated is not None
    assert updated.route_specification.origin == original.route_specification.origin
    assert updated.route_specification.destination == destination
    assert (
        updated.route_specification.arrival_deadline
        == original.route_specification.arrival_deadline
    )
    dashboard = client.get('/admin/dashboard/').content.decode()
    not_routed_table = dashboard.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]
    assert destination.name in not_routed_table


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_update_preserves_other_route_specification_fields(client):
    call_command('seed_sample_data')
    original = cargo_repository.find(TrackingId('DEF789'))
    assert original is not None
    new_deadline = datetime(2031, 2, 3, tzinfo=UTC)

    response = client.post('/admin/cargo/DEF789/deadline/', {'deadline': '2031-02-03'})
    updated = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 302
    assert response.url == '/admin/dashboard/'
    assert updated is not None
    assert updated.route_specification.origin == original.route_specification.origin
    assert updated.route_specification.destination == original.route_specification.destination
    assert updated.route_specification.arrival_deadline == new_deadline.replace(
        hour=0, minute=0, second=0, microsecond=0
    )
