import re
from datetime import date

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.booking.interfaces.dialogs.views import create_booking_dialog_views
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.domain.un_locode import UnLocode
from cargotracker.location.infrastructure.repository import DjangoLocationRepository


cargo_repository = DjangoCargoRepository()
location_repository = DjangoLocationRepository()
dashboard = CargoDashboard(cargo_repository)
specification = CargoSpecification(cargo_repository, DjangoHandlingEventRepository())
destination_view, deadline_view = create_booking_dialog_views(
    specification, dashboard, location_repository.find_all
)
urlpatterns = [
    path('admin/cargo/<str:tracking_id>/destination/', destination_view),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_view),
]


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_shows_current_value_and_filters_options_without_mutation(client):
    call_command('seed_sample_data')
    locations = location_repository.find_all()
    original_locations = list(locations)

    for _ in range(2):
        response = client.get('/admin/cargo/DEF789/destination/')
        content = response.content.decode()

        assert response.status_code == 200
        assert 'Current destination: Melbourne (AUMEL)' in content
        options = re.search(r'<select\b[^>]*>(.*?)</select>', content, re.DOTALL)
        assert options is not None
        option_codes = re.findall(r'<option\b[^>]*value="([^"]+)"', options.group(1))
        assert option_codes == [
            location.unlocode.value
            for location in original_locations
            if location.unlocode.value not in {'CNHKG', 'AUMEL'}
        ]
        assert 'value="AUMEL"' not in options.group(1)

    assert locations == original_locations


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_reports_invalid_date_as_a_field_error(client):
    call_command('seed_sample_data')

    response = client.post('/admin/cargo/DEF789/deadline/', {'deadline': 'not-a-date'})
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Enter a valid arrival deadline.' in content
    assert 'aria-invalid="true"' in content
    assert 'id="deadline-error"' in content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_update_preserves_origin_and_deadline_and_redirects(client):
    call_command('seed_sample_data')
    cargo_before = cargo_repository.find(TrackingId('DEF789'))
    assert cargo_before is not None
    deadline_before = cargo_before.route_specification.arrival_deadline

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'USNYC'},
        HTTP_HX_REQUEST='true',
    )
    cargo_after = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 200
    assert response.headers['HX-Redirect'] == '/admin/dashboard/'
    assert cargo_after is not None
    assert cargo_after.route_specification.origin == cargo_before.route_specification.origin
    assert cargo_after.route_specification.destination == location_repository.find(
        UnLocode('USNYC')
    )
    assert cargo_after.route_specification.arrival_deadline == deadline_before
    assert b'widget' not in response.content.lower()


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_update_preserves_origin_and_destination_and_redirects(client):
    call_command('seed_sample_data')
    cargo_before = cargo_repository.find(TrackingId('DEF789'))
    assert cargo_before is not None

    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': '2030-01-02'},
        HTTP_HX_REQUEST='true',
    )
    cargo_after = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 200
    assert response.headers['HX-Redirect'] == '/admin/dashboard/'
    assert cargo_after is not None
    assert cargo_after.route_specification.origin == cargo_before.route_specification.origin
    assert cargo_after.route_specification.destination == cargo_before.route_specification.destination
    assert cargo_after.route_specification.arrival_deadline.date() == date(2030, 1, 2)
    assert b'widget' not in response.content.lower()
