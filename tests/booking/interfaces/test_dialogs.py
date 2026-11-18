import re

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.booking.interfaces.dialogs.views import create_booking_dialog_views
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository

cargo_repository = DjangoCargoRepository()
location_repository = DjangoLocationRepository()
dashboard = CargoDashboard(cargo_repository)
specification = CargoSpecification(cargo_repository, DjangoHandlingEventRepository())
destination_view, deadline_view = create_booking_dialog_views(
    dashboard, specification, location_repository.find_all
)
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
