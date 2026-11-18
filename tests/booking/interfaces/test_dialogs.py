import re

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.booking.interfaces.dialogs.views import create_destination_dialog_view
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository

cargo_repository = DjangoCargoRepository()
location_repository = DjangoLocationRepository()
dashboard = CargoDashboard(cargo_repository)
destination_dialog_view = create_destination_dialog_view(
    dashboard,
    CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
    location_repository.find_all,
)
urlpatterns = [
    path('admin/cargo/<str:tracking_id>/destination/', destination_dialog_view),
]


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_shows_current_route_specification_and_filtered_options(client):
    call_command('seed_sample_data')

    response = client.get('/admin/cargo/DEF789/destination/')
    content = response.content.decode()
    options = re.search(r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', content, re.DOTALL)

    assert response.status_code == 200
    assert 'Change destination' in content
    assert 'Hong Kong' in content
    assert 'Melbourne' in content
    assert options is not None
    assert 'CNHKG' not in options.group(1)
    assert 'AUMEL' not in options.group(1)


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_destination_dialog_rejects_origin_without_changing_route(client):
    call_command('seed_sample_data')

    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'CNHKG'},
        HTTP_HX_REQUEST='true',
    )
    cargo = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 200
    assert 'Select a valid destination.' in response.content.decode()
    assert 'aria-invalid="true"' in response.content.decode()
    assert cargo is not None
    assert cargo.route_specification.destination.unlocode.value == 'AUMEL'
