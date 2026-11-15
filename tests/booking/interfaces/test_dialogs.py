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
dashboard = CargoDashboard(cargo_repository)
specification = CargoSpecification(cargo_repository, DjangoHandlingEventRepository())
destination_view, deadline_view = create_booking_dialog_views(
    dashboard,
    specification,
    DjangoLocationRepository().find_all,
)
urlpatterns = [
    path('admin/cargo/<str:tracking_id>/destination/', destination_view),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_view),
]


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_shows_current_values_and_stable_filtered_options(client):
    call_command('seed_sample_data')

    first_response = client.get(
        '/admin/cargo/DEF789/destination/',
        HTTP_HX_REQUEST='true',
    )
    second_response = client.get(
        '/admin/cargo/DEF789/destination/',
        HTTP_HX_REQUEST='true',
    )
    first_content = first_response.content.decode()
    options = re.search(
        r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', first_content, re.DOTALL
    )
    repeated_options = re.search(
        r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>',
        second_response.content.decode(),
        re.DOTALL,
    )

    assert first_response.status_code == 200
    assert 'Hong Kong' in first_content
    assert 'Melbourne' in first_content
    assert options is not None
    assert repeated_options is not None
    option_codes = re.findall(r'<option\b[^>]*value="([^"]+)"', options.group(1))
    assert len(option_codes) == 11
    assert 'CNHKG' not in option_codes
    assert 'AUMEL' not in option_codes
    assert options.group(1) == repeated_options.group(1)
