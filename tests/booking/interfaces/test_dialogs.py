import re
from datetime import UTC, datetime

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.booking.interfaces.dialogs.views import create_dialog_views
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository

repository = DjangoCargoRepository()
dashboard = CargoDashboard(repository)
locations = []
destination_dialog, deadline_dialog = create_dialog_views(
    dashboard,
    CargoSpecification(repository, DjangoHandlingEventRepository()),
    lambda: locations,
)
dashboard_view, _ = create_booking_views(dashboard)

urlpatterns = [
    path('admin/dashboard/', dashboard_view),
    path('admin/cargo/<str:tracking_id>/destination/', destination_dialog),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_dialog),
]


def _seed_booking_data():
    call_command('seed_sample_data')
    locations[:] = DjangoLocationRepository().find_all()


@pytest.fixture(autouse=True)
def reset_locations():
    locations.clear()
    yield
    locations.clear()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_not_routed_table_opens_destination_and_deadline_dialogs(client):
    _seed_booking_data()

    response = client.get('/admin/dashboard/')
    table = response.content.decode().split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]

    assert response.status_code == 200
    assert 'href="/admin/cargo/DEF789/route/"' in table
    assert 'href="/admin/cargo/DEF789/destination/"' in table
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in table
    assert 'href="/admin/cargo/DEF789/deadline/"' in table
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in table
    assert 'id="booking-dialog"' in table


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_has_a_full_page_fallback_without_htmx(client):
    _seed_booking_data()

    response = client.get('/admin/cargo/DEF789/destination/')

    assert response.status_code == 200
    assert '<header' in response.content.decode()
    assert 'id="destination"' in response.content.decode()
    assert 'id="booking-dialog"' not in response.content.decode()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_shows_current_values_and_stable_filtered_options(client):
    _seed_booking_data()
    original_locations = locations.copy()

    first = client.get('/admin/cargo/DEF789/destination/')
    second = client.get('/admin/cargo/DEF789/destination/')
    first_options = re.findall(r'<option\b[^>]*>.*?</option>', first.content.decode())
    second_options = re.findall(r'<option\b[^>]*>.*?</option>', second.content.decode())

    assert first.status_code == 200
    assert 'Hong Kong' in first.content.decode()
    assert 'Melbourne' in first.content.decode()
    assert 'destination-error' not in first.content.decode()
    assert 'value="CNHKG"' not in first.content.decode()
    assert 'value="AUMEL"' not in first.content.decode()
    assert 'value="USNYC"' in first.content.decode()
    assert first_options == second_options
    assert locations == original_locations


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_updates_cargo_and_refreshes_not_routed_table(client):
    _seed_booking_data()
    cargo = repository.find(TrackingId('DEF789'))
    assert cargo is not None
    original_deadline = cargo.route_specification.arrival_deadline

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'USNYC'},
        HTTP_HX_REQUEST='true',
    )

    updated = repository.find(TrackingId('DEF789'))
    assert updated is not None
    assert response.status_code == 200
    assert response['HX-Retarget'] == '#not-routed-cargo'
    assert response['HX-Reswap'] == 'outerHTML'
    assert 'New York' in response.content.decode()
    assert updated.route_specification.origin == cargo.route_specification.origin
    assert updated.route_specification.destination.unlocode.value == 'USNYC'
    assert updated.route_specification.arrival_deadline == original_deadline
    assert updated.itinerary == cargo.itinerary
    assert 'Widget for var' not in response.content.decode()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_form_redirects_to_dashboard_without_htmx(client):
    _seed_booking_data()

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'USNYC'},
    )

    updated = repository.find(TrackingId('DEF789'))
    assert updated is not None
    assert response.status_code == 302
    assert response['Location'] == '/admin/dashboard/'
    assert updated.route_specification.destination.unlocode.value == 'USNYC'


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_rejects_origin_as_a_new_destination(client):
    _seed_booking_data()
    cargo = repository.find(TrackingId('DEF789'))
    assert cargo is not None

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': cargo.route_specification.origin.unlocode.value},
    )

    unchanged = repository.find(TrackingId('DEF789'))
    assert unchanged is not None
    assert response.status_code == 200
    assert 'Select a valid destination.' in response.content.decode()
    assert 'aria-invalid="true"' in response.content.decode()
    assert unchanged.route_specification.destination == cargo.route_specification.destination


@pytest.mark.django_db
@pytest.mark.xfail(
    strict=True,
    reason='The application use case accepts a destination excluded by the destination-options rule.',
)
def test_cargo_specification_rejects_current_destination():
    _seed_booking_data()
    cargo = repository.find(TrackingId('DEF789'))
    assert cargo is not None

    with pytest.raises(ValueError):
        CargoSpecification(repository, DjangoHandlingEventRepository()).change_destination(
            cargo.tracking_id, cargo.route_specification.destination
        )


@pytest.mark.django_db
def test_cargo_specification_rejects_non_datetime_deadline():
    _seed_booking_data()
    cargo = repository.find(TrackingId('DEF789'))
    assert cargo is not None

    with pytest.raises(TypeError, match='Arrival deadline must be a datetime'):
        CargoSpecification(repository, DjangoHandlingEventRepository()).change_deadline(
            cargo.tracking_id, 'not-a-date'
        )

    unchanged = repository.find(cargo.tracking_id)
    assert unchanged is not None
    assert unchanged.route_specification.arrival_deadline == cargo.route_specification.arrival_deadline


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_shows_initial_value_and_parse_error_without_updating(client):
    _seed_booking_data()
    cargo = repository.find(TrackingId('DEF789'))
    assert cargo is not None
    initial_deadline = cargo.route_specification.arrival_deadline

    initial = client.get('/admin/cargo/DEF789/deadline/')
    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': 'not-a-date'},
        HTTP_HX_REQUEST='true',
    )

    unchanged = repository.find(TrackingId('DEF789'))
    assert unchanged is not None
    assert initial.status_code == 200
    assert 'Hong Kong' in initial.content.decode()
    assert 'Melbourne' in initial.content.decode()
    assert 'deadline-error' not in initial.content.decode()
    assert f'value="{initial_deadline:%Y-%m-%d}"' in initial.content.decode()
    assert response.status_code == 200
    assert 'Enter a valid arrival deadline.' in response.content.decode()
    assert 'aria-invalid="true"' in response.content.decode()
    assert unchanged.route_specification.arrival_deadline == initial_deadline


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_updates_cargo_and_refreshes_table(client):
    _seed_booking_data()
    cargo = repository.find(TrackingId('DEF789'))
    assert cargo is not None

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': '2027-01-15'},
        HTTP_HX_REQUEST='true',
    )

    updated = repository.find(TrackingId('DEF789'))
    assert updated is not None
    assert response.status_code == 200
    assert response['HX-Retarget'] == '#not-routed-cargo'
    assert response['HX-Reswap'] == 'outerHTML'
    assert '01/15/2027' in response.content.decode()
    assert updated.route_specification.origin == cargo.route_specification.origin
    assert updated.route_specification.destination == cargo.route_specification.destination
    assert updated.route_specification.arrival_deadline == datetime(2027, 1, 15, tzinfo=UTC)
    assert updated.itinerary == cargo.itinerary
    assert 'Widget for var' not in response.content.decode()


@pytest.mark.parametrize(
    'url',
    (
        '/admin/cargo/MISSING1/destination/',
        '/admin/cargo/MISSING1/deadline/',
    ),
)
@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_dialogs_return_not_found_for_unknown_cargo(client, url):
    response = client.get(url)

    assert response.status_code == 404


@pytest.mark.parametrize(
    'url',
    (
        '/admin/cargo/DEF789/destination/',
        '/admin/cargo/DEF789/deadline/',
    ),
)
@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_dialogs_reject_unsupported_methods(client, url):
    response = client.put(url)

    assert response.status_code == 405
    assert response['Allow'] == 'GET, POST'
