import re

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.interfaces.dialogs.views import (
    create_deadline_dialog_view,
    create_destination_dialog_view,
)
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.location.infrastructure.repository import DjangoLocationRepository

cargo_repository = DjangoCargoRepository()
location_repository = DjangoLocationRepository()
dashboard = CargoDashboard(cargo_repository)
destination_view = create_destination_dialog_view(dashboard, location_repository.find_all)
deadline_view = create_deadline_dialog_view(dashboard)
urlpatterns = [
    path('admin/cargo/<str:tracking_id>/destination/', destination_view),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_view),
]


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_filters_options_without_mutating_locations(client):
    call_command('seed_sample_data')
    locations_before = location_repository.find_all()

    response = client.get('/admin/cargo/DEF789/destination/')
    second_response = client.get('/admin/cargo/DEF789/destination/')

    assert response.status_code == 200
    content = response.content.decode()
    select = re.search(r'<select\b.*?</select>', content, re.DOTALL).group()
    option_codes = re.findall(r'<option value="([^"]+)"', select)

    assert 'Hong Kong' in content
    assert 'Melbourne' in content
    assert 'CNHKG' not in option_codes
    assert 'AUMEL' not in option_codes
    assert locations_before == location_repository.find_all()
    assert response.content == second_response.content


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_deadline_dialog_shows_current_route_and_deadline(client):
    call_command('seed_sample_data')

    response = client.get('/admin/cargo/DEF789/deadline/')
    cargo = dashboard.get_cargo_details(TrackingId('DEF789'))

    assert response.status_code == 200
    content = response.content.decode()
    assert cargo is not None
    assert cargo.route_specification.origin.name in content
    assert cargo.route_specification.destination.name in content
    assert f'value="{cargo.route_specification.arrival_deadline.date().isoformat()}"' in content
