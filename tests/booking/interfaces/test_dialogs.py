import re
from datetime import timedelta

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.urls import path
from django.utils import timezone

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.booking.interfaces.dialogs.views import create_dialog_views
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository

cargo_repository = DjangoCargoRepository()
location_repository = DjangoLocationRepository()
dashboard_view, cargo_details_view = create_booking_views(CargoDashboard(cargo_repository))
destination_dialog_view, deadline_dialog_view = create_dialog_views(
    CargoDashboard(cargo_repository),
    CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
    lambda: location_repository.find_all(),
)
urlpatterns = [
    path('admin/dashboard/', dashboard_view),
    path('admin/cargo/<str:tracking_id>/', cargo_details_view),
    path('admin/cargo/<str:tracking_id>/destination/', destination_dialog_view),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_dialog_view),
]


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_shows_current_values_and_stable_filtered_options(client, monkeypatch):
    call_command('seed_sample_data')
    locations = location_repository.find_all()
    original_codes = [location.unlocode.value for location in locations]
    monkeypatch.setattr(location_repository, 'find_all', lambda: locations)

    responses = [
        client.get('/admin/cargo/DEF789/destination/'),
        client.get('/admin/cargo/DEF789/destination/'),
    ]
    contents = [response.content.decode() for response in responses]

    assert all(response.status_code == 200 for response in responses)
    assert all('Hong Kong' in content and 'Melbourne' in content for content in contents)
    options = [
        re.search(r'<select\b[^>]*>(.*?)</select>', content, re.DOTALL).group(1)
        for content in contents
    ]
    assert options[0] == options[1]
    option_values = re.findall(r'<option value="([^"]+)"', options[0])
    assert 'CNHKG' not in option_values
    assert 'AUMEL' not in option_values
    assert 'FIHEL' in option_values
    assert [location.unlocode.value for location in locations] == original_codes


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_shows_current_deadline_and_parse_error(client):
    call_command('seed_sample_data')
    cargo = cargo_repository.find(TrackingId('DEF789'))
    assert cargo is not None
    current_deadline = cargo.route_specification.arrival_deadline.date().isoformat()

    initial = client.get('/admin/cargo/DEF789/deadline/')
    invalid = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': 'not-a-date'},
        HTTP_HX_REQUEST='true',
    )

    assert initial.status_code == 200
    assert f'value="{current_deadline}"' in initial.content.decode()
    assert invalid.status_code == 200
    assert 'Enter a valid arrival deadline.' in invalid.content.decode()
    assert 'deadline-error' in invalid.content.decode()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_update_preserves_other_fields_and_refreshes_dashboard(client):
    call_command('seed_sample_data')
    original = cargo_repository.find(TrackingId('DEF789'))
    assert original is not None
    original_deadline = original.route_specification.arrival_deadline.date()

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'FIHEL'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 204
    assert response['HX-Redirect'] == '/admin/dashboard/'
    assert 'Widget for var' not in response.content.decode()
    dashboard = client.get(response['HX-Redirect']).content.decode()
    row = dashboard.split('data-tracking-id="DEF789"', 1)[1].split('</tr>', 1)[0]
    assert 'Hong Kong' in row
    assert 'Helsinki' in row
    assert original_deadline.strftime('%m/%d/%Y') in row


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_update_preserves_other_fields_and_refreshes_dashboard(client):
    call_command('seed_sample_data')
    original = cargo_repository.find(TrackingId('DEF789'))
    assert original is not None
    new_deadline = timezone.localdate() + timedelta(days=30)

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': new_deadline.isoformat()},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 204
    assert response['HX-Redirect'] == '/admin/dashboard/'
    dashboard = client.get(response['HX-Redirect']).content.decode()
    row = dashboard.split('data-tracking-id="DEF789"', 1)[1].split('</tr>', 1)[0]
    assert 'Hong Kong' in row
    assert 'Melbourne' in row
    assert new_deadline.strftime('%m/%d/%Y') in row
    assert 'Widget for var' not in response.content.decode()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_not_routed_table_opens_destination_and_deadline_dialogs(client):
    call_command('seed_sample_data')

    response = client.get('/admin/dashboard/')
    content = response.content.decode()
    not_routed_table = content.split('id="not-routed-cargo"', 1)[1].split('</section>', 1)[0]

    assert response.status_code == 200
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in not_routed_table
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in not_routed_table
    assert 'id="cargo-edit-dialog"' in not_routed_table
