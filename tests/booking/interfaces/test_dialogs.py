import re

import pytest
from django.core.management import call_command
from django.template.loader import render_to_string
from django.test import RequestFactory, override_settings
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.booking.interfaces.dialogs.views import create_booking_dialog_views
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository

_http_repository = DjangoCargoRepository()
_http_destination_view, _http_deadline_view = create_booking_dialog_views(
    CargoDashboard(_http_repository),
    CargoSpecification(_http_repository, DjangoHandlingEventRepository()),
    DjangoLocationRepository().find_all,
)
urlpatterns = [
    path('admin/cargo/<str:tracking_id>/destination/', _http_destination_view),
    path('admin/cargo/<str:tracking_id>/deadline/', _http_deadline_view),
]


@pytest.mark.django_db
def test_destination_dialog_shows_current_values_and_keeps_filtered_options_stable():
    call_command('seed_sample_data')
    cargo_repository = DjangoCargoRepository()
    locations = DjangoLocationRepository().find_all()
    original_locations = locations.copy()
    destination_view, _ = create_booking_dialog_views(
        CargoDashboard(cargo_repository),
        CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
        lambda: locations,
    )
    request_factory = RequestFactory()

    responses = [
        destination_view(request_factory.get('/admin/cargo/DEF789/destination/'), 'DEF789')
        for _ in range(2)
    ]

    assert locations == original_locations
    for response in responses:
        content = response.content.decode()
        options = re.search(r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', content, re.DOTALL)
        assert response.status_code == 200
        assert 'Hong Kong' in content and 'CNHKG' in content
        assert 'Melbourne' in content and 'AUMEL' in content
        assert options is not None
        assert 'value="CNHKG"' not in options.group(1)
        assert 'value="AUMEL"' not in options.group(1)
        assert options.group(1).count('<option') == 12


@pytest.mark.django_db
def test_destination_update_preserves_other_route_fields_and_refreshes_not_routed_table():
    call_command('seed_sample_data')
    cargo_repository = DjangoCargoRepository()
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    destination_view, _ = create_booking_dialog_views(
        CargoDashboard(cargo_repository),
        CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
        DjangoLocationRepository().find_all,
    )

    invalid_response = destination_view(
        RequestFactory().post(
            '/admin/cargo/DEF789/destination/',
            {'destination': 'CNHKG'},
        ),
        'DEF789',
    )
    unchanged = cargo_repository.find(cargo.tracking_id)

    assert invalid_response.status_code == 200
    assert 'Select a valid destination.' in invalid_response.content.decode()
    assert 'aria-invalid="true"' in invalid_response.content.decode()
    assert unchanged is not None
    assert unchanged.route_specification == cargo.route_specification

    response = destination_view(
        RequestFactory().post(
            '/admin/cargo/DEF789/destination/',
            {'destination': 'USNYC'},
            HTTP_HX_REQUEST='true',
        ),
        'DEF789',
    )
    updated = cargo_repository.find(cargo.tracking_id)

    assert response.status_code == 200
    assert response.headers['HX-Retarget'] == '#not-routed-cargo'
    assert response.headers['HX-Reswap'] == 'outerHTML'
    assert 'New York' in response.content.decode()
    assert updated is not None
    assert updated.route_specification.origin == cargo.route_specification.origin
    assert updated.route_specification.destination.unlocode.value == 'USNYC'
    assert updated.route_specification.arrival_deadline == cargo.route_specification.arrival_deadline


@pytest.mark.django_db
def test_deadline_dialog_reports_invalid_dates_and_updates_the_not_routed_row():
    call_command('seed_sample_data')
    cargo_repository = DjangoCargoRepository()
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    _, deadline_view = create_booking_dialog_views(
        CargoDashboard(cargo_repository),
        CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
        DjangoLocationRepository().find_all,
    )
    request_factory = RequestFactory()

    initial_response = deadline_view(
        request_factory.get('/admin/cargo/DEF789/deadline/'),
        'DEF789',
    )
    initial_content = initial_response.content.decode()

    assert initial_response.status_code == 200
    assert 'Hong Kong' in initial_content and 'Melbourne' in initial_content
    assert f'value="{cargo.route_specification.arrival_deadline.date().isoformat()}"' in (
        initial_content
    )

    invalid_response = deadline_view(
        request_factory.post(
            '/admin/cargo/DEF789/deadline/',
            {'deadline': 'not-a-date'},
        ),
        'DEF789',
    )

    assert invalid_response.status_code == 200
    assert 'Enter a valid arrival deadline.' in invalid_response.content.decode()
    assert 'aria-invalid="true"' in invalid_response.content.decode()
    assert cargo_repository.find(cargo.tracking_id).route_specification.arrival_deadline == (
        cargo.route_specification.arrival_deadline
    )

    response = deadline_view(
        request_factory.post(
            '/admin/cargo/DEF789/deadline/',
            {'deadline': '2026-01-15'},
            HTTP_HX_REQUEST='true',
        ),
        'DEF789',
    )
    updated = cargo_repository.find(cargo.tracking_id)

    assert response.status_code == 200
    assert response.headers['HX-Retarget'] == '#not-routed-cargo'
    assert response.headers['HX-Reswap'] == 'outerHTML'
    assert '01/15/2026' in response.content.decode()
    assert 'Widget for var' not in response.content.decode()
    assert updated is not None
    assert updated.route_specification.origin == cargo.route_specification.origin
    assert updated.route_specification.destination == cargo.route_specification.destination
    assert updated.route_specification.arrival_deadline.date().isoformat() == '2026-01-15'


@pytest.mark.django_db
def test_not_routed_table_opens_destination_and_deadline_dialogs():
    call_command('seed_sample_data')
    cargo = DjangoCargoRepository().find(TrackingId('DEF789'))
    assert cargo is not None

    content = render_to_string(
        'booking/dashboard/not_routed_table.html',
        {'not_routed_cargos': [cargo]},
    )

    assert 'hx-get="/admin/cargo/DEF789/destination/"' in content
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in content
    assert 'hx-target="#booking-dialog"' in content
    assert 'id="booking-dialog"' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_http_deadline_dialog_updates_and_refreshes_the_table(client):
    call_command('seed_sample_data')

    initial_response = client.get('/admin/cargo/DEF789/deadline/')
    assert initial_response.status_code == 200
    assert 'Hong Kong' in initial_response.content.decode()

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': '2026-01-15'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert response.headers['HX-Retarget'] == '#not-routed-cargo'
    assert '01/15/2026' in response.content.decode()
