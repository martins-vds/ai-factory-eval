import re

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.booking.interfaces.dialogs.views import create_booking_dialog_views
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository

cargo_repository = DjangoCargoRepository()
location_repository = DjangoLocationRepository()
dashboard = CargoDashboard(cargo_repository)
dashboard_view, _ = create_booking_views(dashboard)
destination_dialog_view, deadline_dialog_view = create_booking_dialog_views(
    dashboard,
    CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
    location_repository.find_all,
)

urlpatterns = [
    path('admin/dashboard/', dashboard_view),
    path('admin/cargo/<str:tracking_id>/destination/', destination_dialog_view),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_dialog_view),
]


@pytest.fixture(autouse=True)
def sample_data(db):
    call_command('seed_sample_data')


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_not_routed_table_opens_both_edit_dialogs(client):
    content = client.get('/admin/dashboard/').content.decode()

    assert 'Change destination' in content
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in content
    assert 'Change deadline' in content
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in content
    assert 'id="booking-dialog"' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_shows_initial_values_and_stable_filtered_options(client):
    locations_before = location_repository.find_all()
    first = client.get(
        '/admin/cargo/DEF789/destination/',
        HTTP_HX_REQUEST='true',
    ).content.decode()
    second = client.get(
        '/admin/cargo/DEF789/destination/',
        HTTP_HX_REQUEST='true',
    ).content.decode()

    first_options = re.search(
        r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', first, re.DOTALL
    )
    second_options = re.search(
        r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', second, re.DOTALL
    )
    assert first_options is not None
    assert second_options is not None
    option_values = re.findall(r'<option\b[^>]*value="([^"]+)"', first_options.group(1))

    assert 'Hong Kong' in first and 'Melbourne' in first
    assert 'CNHKG' not in option_values
    assert 'AUMEL' not in option_values
    assert option_values == re.findall(r'<option\b[^>]*value="([^"]+)"', second_options.group(1))
    assert location_repository.find_all() == locations_before


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_shows_the_cargos_current_deadline(client):
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None

    response = client.get(
        '/admin/cargo/DEF789/deadline/',
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert f'value="{cargo.route_specification.arrival_deadline:%Y-%m-%d}"' in (
        response.content.decode()
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_unparseable_deadline_shows_a_field_error_without_changing_cargo(client):
    original = cargo_repository.find(TrackingId('DEF789'))
    assert original is not None

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': '2027-02-31'},
        HTTP_HX_REQUEST='true',
    )
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Enter a valid arrival deadline.' in content
    assert 'id="deadline-error"' in content
    assert 'aria-invalid="true"' in content
    assert 'aria-describedby="deadline-error"' in content
    assert cargo_repository.find(TrackingId('DEF789')) == original


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_update_preserves_other_specification_fields_and_refreshes_rows(client):
    original = cargo_repository.find(TrackingId('DEF789'))
    assert original is not None

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'USNYC'},
        HTTP_HX_REQUEST='true',
    )
    updated = cargo_repository.find(TrackingId('DEF789'))
    content = response.content.decode()
    refreshed_dashboard = client.get('/admin/dashboard/').content.decode()
    not_routed_rows = content.split('id="not-routed-cargo-rows"', 1)[1]

    assert response.status_code == 200
    assert 'hx-swap-oob="innerHTML"' in content
    assert '<dialog' not in content
    assert 'Widget for var' not in content
    assert 'New York' in not_routed_rows
    assert updated is not None
    assert updated.route_specification.destination.unlocode.value == 'USNYC'
    assert updated.route_specification.origin == original.route_specification.origin
    assert updated.route_specification.arrival_deadline == (
        original.route_specification.arrival_deadline
    )
    assert 'New York' in refreshed_dashboard


@pytest.mark.django_db
def test_change_destination_use_case_rejects_the_cargos_origin():
    original = cargo_repository.find(TrackingId('DEF789'))
    assert original is not None

    with pytest.raises(ValueError, match="Origin and destination can't be the same"):
        CargoSpecification(cargo_repository, DjangoHandlingEventRepository()).change_destination(
            TrackingId('DEF789'),
            original.route_specification.origin,
        )

    assert cargo_repository.find(TrackingId('DEF789')) == original


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_reports_when_the_origin_is_submitted(client):
    original = cargo_repository.find(TrackingId('DEF789'))
    assert original is not None

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': original.route_specification.origin.unlocode.value},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert 'Destination must differ from origin.' in response.content.decode()
    assert cargo_repository.find(TrackingId('DEF789')) == original


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_update_preserves_other_specification_fields_and_completes_dialog(client):
    original = cargo_repository.find(TrackingId('DEF789'))
    assert original is not None

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': '2027-01-15'},
        HTTP_HX_REQUEST='true',
    )
    updated = cargo_repository.find(TrackingId('DEF789'))
    content = response.content.decode()
    not_routed_rows = content.split('id="not-routed-cargo-rows"', 1)[1]

    assert response.status_code == 200
    assert 'hx-swap-oob="innerHTML"' in content
    assert '<dialog' not in content
    assert 'Widget for var' not in content
    assert '01/15/2027' in not_routed_rows
    assert updated is not None
    assert updated.route_specification.arrival_deadline.date().isoformat() == '2027-01-15'
    assert updated.route_specification.origin == original.route_specification.origin
    assert updated.route_specification.destination == original.route_specification.destination
