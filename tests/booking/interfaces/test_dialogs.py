import re

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.booking.interfaces.dialogs.views import (
    create_deadline_dialog_view,
    create_destination_dialog_view,
)
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository

cargo_repository = DjangoCargoRepository()
dashboard_view, _ = create_booking_views(CargoDashboard(cargo_repository))
shipping_locations = []
destination_dialog_view = create_destination_dialog_view(
    CargoDashboard(cargo_repository),
    CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
    lambda: shipping_locations,
)
deadline_dialog_view = create_deadline_dialog_view(
    CargoDashboard(cargo_repository),
    CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
)
urlpatterns = [
    path('admin/dashboard/', dashboard_view),
    path('admin/cargo/<str:tracking_id>/destination/', destination_dialog_view),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_dialog_view),
]


@pytest.fixture(autouse=True)
def seed_booking_data():
    call_command('seed_sample_data')
    shipping_locations[:] = DjangoLocationRepository().find_all()
    yield
    shipping_locations.clear()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_not_routed_cargo_opens_destination_and_deadline_dialogs(client):
    response = client.get('/admin/dashboard/')
    content = response.content.decode()
    not_routed_table = content.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]

    assert response.status_code == 200
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in not_routed_table
    assert 'aria-haspopup="dialog"' in not_routed_table
    assert 'aria-controls="cargo-edit-dialog"' in not_routed_table
    assert '<dialog' in not_routed_table
    assert 'id="cargo-edit-dialog"' in not_routed_table
    assert 'hx-on::after-swap=' in not_routed_table


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_excludes_origin_and_current_destination_without_mutating_locations(
    client,
):
    original_locations = tuple(location.unlocode.value for location in shipping_locations)

    response = client.get('/admin/cargo/DEF789/destination/')
    first_content = response.content.decode()
    first_options = re.findall(r'<option\b[^>]*value="([^"]+)"', first_content)
    second_content = client.get('/admin/cargo/DEF789/destination/').content.decode()
    second_options = re.findall(r'<option\b[^>]*value="([^"]+)"', second_content)

    assert response.status_code == 200
    assert 'Hong Kong' in first_content
    assert 'Melbourne' in first_content
    assert 'hx-post="/admin/cargo/DEF789/destination/"' in first_content
    assert 'method="dialog"' in first_content
    assert 'CNHKG' not in first_options
    assert 'AUMEL' not in first_options
    assert 'USDAL' in first_options
    assert 'id="destination-error"' not in first_content
    assert first_options == second_options
    assert tuple(location.unlocode.value for location in shipping_locations) == original_locations


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
@pytest.mark.parametrize('destination', ['CNHKG', 'AUMEL', 'UNKNOWN'])
def test_destination_dialog_rejects_unavailable_destinations_without_updating_cargo(
    client, destination
):
    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': destination},
        HTTP_HX_REQUEST='true',
    )
    content = response.content.decode()

    assert response.status_code == 200
    assert '>Select a valid destination.</p>' in content
    assert 'aria-invalid="true"' in content
    assert 'HX-Redirect' not in response
    cargo = CargoDashboard(cargo_repository).get_cargo_details(TrackingId('DEF789'))
    assert cargo is not None
    assert cargo.route_specification.destination.unlocode.value == 'AUMEL'


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
@pytest.mark.parametrize(
    'path',
    [
        '/admin/cargo/DEF789/destination/',
        '/admin/cargo/DEF789/deadline/',
    ],
)
def test_dialogs_reject_unsupported_methods(client, path):
    response = client.put(path)

    assert response.status_code == 405


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_rejects_missing_field(client):
    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert '>Select a valid destination.</p>' in response.content.decode()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_updates_cargo_and_refreshes_dashboard(client):
    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'USDAL'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert response['HX-Redirect'] == '/admin/dashboard/'
    assert 'PrimeFaces' not in response.content.decode()
    cargo = CargoDashboard(cargo_repository).get_cargo_details(TrackingId('DEF789'))
    assert cargo is not None
    assert cargo.route_specification.origin.unlocode.value == 'CNHKG'
    assert cargo.route_specification.destination.unlocode.value == 'USDAL'
    assert cargo.route_specification.arrival_deadline.date().isoformat() == '2027-01-18'
    assert 'console.warn' not in response.content.decode()
    dashboard = client.get('/admin/dashboard/').content.decode()
    not_routed_table = dashboard.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]
    assert 'Dallas' in not_routed_table


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_redirects_after_non_htmx_update(client):
    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'USDAL'},
    )

    assert response.status_code == 302
    assert response['Location'] == '/admin/dashboard/'


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_displays_route_and_current_deadline(client):
    response = client.get('/admin/cargo/DEF789/deadline/')
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Hong Kong' in content
    assert 'Melbourne' in content
    assert 'type="date"' in content
    assert 'value="2027-01-18"' in content
    assert 'hx-post="/admin/cargo/DEF789/deadline/"' in content
    assert 'id="deadline-error"' not in content
    assert 'method="dialog"' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
@pytest.mark.parametrize('deadline', ['not-a-date', '2027-02-30', ''])
def test_deadline_dialog_renders_parse_error_without_changing_cargo(client, deadline):
    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': deadline},
        HTTP_HX_REQUEST='true',
    )
    content = response.content.decode()

    assert response.status_code == 200
    assert '>Enter a valid arrival deadline.</p>' in content
    assert 'id="deadline-error"' in content
    assert 'aria-invalid="true"' in content
    assert 'HX-Redirect' not in response
    cargo = CargoDashboard(cargo_repository).get_cargo_details(TrackingId('DEF789'))
    assert cargo is not None
    assert cargo.route_specification.arrival_deadline.date().isoformat() == '2027-01-18'


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_rejects_missing_field(client):
    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    content = response.content.decode()
    assert '>Enter a valid arrival deadline.</p>' in content
    assert 'value=""' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_updates_deadline_and_refreshes_rows(client):
    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': '2027-02-01'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert response['HX-Redirect'] == '/admin/dashboard/'
    assert 'PrimeFaces' not in response.content.decode()
    cargo = CargoDashboard(cargo_repository).get_cargo_details(TrackingId('DEF789'))
    assert cargo is not None
    assert cargo.route_specification.origin.unlocode.value == 'CNHKG'
    assert cargo.route_specification.destination.unlocode.value == 'AUMEL'
    assert cargo.route_specification.arrival_deadline.date().isoformat() == '2027-02-01'
    assert 'console.warn' not in response.content.decode()
    dashboard = client.get('/admin/dashboard/').content.decode()
    not_routed_table = dashboard.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]
    assert '02/01/2027' in not_routed_table


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_not_found_dialog_displays_requested_tracking_id(client):
    response = client.get('/admin/cargo/MISSING1/destination/')

    assert response.status_code == 404
    assert 'No cargo exists with tracking ID MISSING1.' in response.content.decode()


@pytest.mark.django_db
def test_destination_use_case_rejects_origin_as_destination():
    cargo = CargoDashboard(cargo_repository).get_cargo_details(TrackingId('DEF789'))
    assert cargo is not None

    with pytest.raises(ValueError, match="Origin and destination can't be the same"):
        CargoSpecification(
            cargo_repository,
            DjangoHandlingEventRepository(),
        ).change_destination(cargo.tracking_id, cargo.route_specification.origin)


@pytest.mark.django_db
def test_deadline_use_case_rejects_non_datetime_input():
    with pytest.raises(TypeError, match='Arrival deadline must be a datetime'):
        CargoSpecification(
            cargo_repository,
            DjangoHandlingEventRepository(),
        ).change_deadline(TrackingId('DEF789'), 'not-a-datetime')


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
@pytest.mark.parametrize(
    'path',
    [
        '/admin/cargo/MISSING1/destination/',
        '/admin/cargo/MISSING1/deadline/',
    ],
)
def test_dialogs_render_not_found_for_unknown_cargo(client, path):
    response = client.get(path)

    assert response.status_code == 404
    assert 'Cargo not found' in response.content.decode()
