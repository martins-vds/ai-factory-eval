import re

import pytest
from django.core.management import call_command
from django.http import Http404
from django.test import Client, RequestFactory, override_settings
from django.urls import path

from cargotracker.booking.application.dashboard import CargoDashboard
from cargotracker.booking.application.specification import CargoSpecification
from cargotracker.booking.interfaces.dashboard.views import create_booking_views
from cargotracker.booking.interfaces.dialogs.views import create_dialog_views
from cargotracker.cargo.domain.tracking_id import TrackingId
from cargotracker.cargo.infrastructure.repository import DjangoCargoRepository
from cargotracker.handling.infrastructure.repository import DjangoHandlingEventRepository
from cargotracker.location.infrastructure.repository import DjangoLocationRepository

application_cargo_repository = DjangoCargoRepository()
application_dashboard = CargoDashboard(application_cargo_repository)
dashboard_view, cargo_details_view = create_booking_views(application_dashboard)
destination_dialog_view, deadline_dialog_view = create_dialog_views(
    CargoSpecification(application_cargo_repository, DjangoHandlingEventRepository()),
    application_dashboard,
    DjangoLocationRepository().find_all,
)
urlpatterns = [
    path('admin/dashboard/', dashboard_view),
    path('admin/cargo/<str:tracking_id>/', cargo_details_view),
    path('admin/cargo/<str:tracking_id>/destination/', destination_dialog_view),
    path('admin/cargo/<str:tracking_id>/deadline/', deadline_dialog_view),
]


def build_dialog_views(locations=None):
    cargo_repository = DjangoCargoRepository()
    location_repository = DjangoLocationRepository()
    return create_dialog_views(
        CargoSpecification(cargo_repository, DjangoHandlingEventRepository()),
        CargoDashboard(cargo_repository),
        locations if locations is not None else location_repository.find_all,
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_not_routed_table_opens_destination_and_deadline_dialogs(client: Client):
    call_command('seed_sample_data')
    content = client.get('/admin/dashboard/').content.decode()

    assert 'Change destination' in content
    assert 'hx-get="/admin/cargo/DEF789/destination/"' in content
    assert 'Change deadline' in content
    assert 'hx-get="/admin/cargo/DEF789/deadline/"' in content
    assert 'hx-target="#cargo-edit-dialog"' in content
    assert 'hx-on::after-swap=' in content
    assert 'hx-on::response-error=' in content
    destination_response = client.get(
        '/admin/cargo/DEF789/destination/',
        HTTP_HX_REQUEST='true',
    )
    deadline_response = client.get(
        '/admin/cargo/DEF789/deadline/',
        HTTP_HX_REQUEST='true',
    )

    assert destination_response.status_code == 200
    destination_content = destination_response.content.decode()
    assert '<dialog' in destination_content
    assert 'destination-error' not in destination_content
    assert deadline_response.status_code == 200
    deadline_content = deadline_response.content.decode()
    assert '<dialog' in deadline_content
    assert 'deadline-error' not in deadline_content


@pytest.mark.django_db
def test_destination_dialog_displays_current_route_and_filters_options_stably():
    call_command('seed_sample_data')
    locations = DjangoLocationRepository().find_all()
    original_locations = list(locations)
    destination_view, _ = build_dialog_views(lambda: locations)

    responses = [
        destination_view(
            RequestFactory().get('/admin/cargo/DEF789/destination/'),
            'DEF789',
        )
        for _ in range(2)
    ]
    contents = [response.content.decode() for response in responses]
    option_lists = [
        re.search(r'<select\b[^>]*name="destination"[^>]*>(.*?)</select>', content, re.DOTALL)
        for content in contents
    ]

    assert all(response.status_code == 200 for response in responses)
    assert all('Hong Kong' in content and 'Melbourne' in content for content in contents)
    assert all(option_list is not None for option_list in option_lists)
    assert all('value="USDAL"' in option_list.group(1) for option_list in option_lists)
    assert all('CNHKG' not in option_list.group(1) for option_list in option_lists)
    assert all('AUMEL' not in option_list.group(1) for option_list in option_lists)
    assert 'value="" disabled selected' in contents[0]
    assert option_lists[0].group(1) == option_lists[1].group(1)
    assert locations == original_locations


@pytest.mark.django_db
def test_destination_dialog_updates_cargo_and_completes_htmx_dialog():
    call_command('seed_sample_data')
    destination_view, _ = build_dialog_views()
    cargo_repository = DjangoCargoRepository()
    original_cargo = cargo_repository.find(TrackingId('DEF789'))
    assert original_cargo is not None

    response = destination_view(
        RequestFactory().post(
            '/admin/cargo/DEF789/destination/',
            {'destination': 'USDAL'},
            HTTP_HX_REQUEST='true',
        ),
        'DEF789',
    )
    updated_cargo = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 204
    assert response['HX-Redirect'] == '/admin/dashboard/'
    assert response.content == b''
    assert updated_cargo is not None
    assert updated_cargo.route_specification.origin == original_cargo.route_specification.origin
    assert updated_cargo.route_specification.destination.unlocode.value == 'USDAL'
    assert updated_cargo.route_specification.arrival_deadline == (
        original_cargo.route_specification.arrival_deadline
    )


@pytest.mark.django_db
def test_destination_dialog_redirects_after_non_htmx_update():
    call_command('seed_sample_data')
    destination_view, _ = build_dialog_views()

    response = destination_view(
        RequestFactory().post(
            '/admin/cargo/DEF789/destination/',
            {'destination': 'USDAL'},
        ),
        'DEF789',
    )

    assert response.status_code == 302
    assert response['Location'] == '/admin/dashboard/'


@pytest.mark.django_db
def test_destination_dialog_refuses_origin_as_a_new_destination():
    call_command('seed_sample_data')
    destination_view, _ = build_dialog_views()

    response = destination_view(
        RequestFactory().post(
            '/admin/cargo/DEF789/destination/',
            {'destination': 'CNHKG'},
            HTTP_HX_REQUEST='true',
        ),
        'DEF789',
    )
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Select a valid destination.' in content
    assert 'aria-invalid="true" aria-describedby="destination-error"' in content


@pytest.mark.django_db
def test_deadline_dialog_displays_current_route_and_deadline():
    call_command('seed_sample_data')
    _, deadline_view = build_dialog_views()
    cargo = DjangoCargoRepository().find(TrackingId('DEF789'))
    assert cargo is not None

    response = deadline_view(
        RequestFactory().get('/admin/cargo/DEF789/deadline/'),
        'DEF789',
    )
    content = response.content.decode()

    assert response.status_code == 200
    assert 'Hong Kong' in content
    assert 'Melbourne' in content
    assert f'value="{cargo.route_specification.arrival_deadline.strftime("%Y-%m-%d")}"' in content
    assert 'deadline-error' not in content


@pytest.mark.parametrize(
    ('deadline', 'error'),
    [
        ('not-a-date', 'Enter a valid arrival deadline.'),
        ('', 'Choose an arrival deadline.'),
    ],
)
@pytest.mark.django_db
def test_deadline_dialog_shows_parse_errors_without_updating_cargo(deadline, error):
    call_command('seed_sample_data')
    _, deadline_view = build_dialog_views()
    cargo_repository = DjangoCargoRepository()
    original_cargo = cargo_repository.find(TrackingId('DEF789'))
    assert original_cargo is not None

    response = deadline_view(
        RequestFactory().post(
            '/admin/cargo/DEF789/deadline/',
            {'deadline': deadline},
            HTTP_HX_REQUEST='true',
        ),
        'DEF789',
    )
    content = response.content.decode()
    unchanged_cargo = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 200
    assert error in content
    assert f'value="{deadline}"' in content
    assert 'id="deadline-error"' in content
    assert 'role="alert"' in content
    assert 'aria-invalid="true" aria-describedby="deadline-error"' in content
    assert unchanged_cargo is not None
    assert (
        unchanged_cargo.route_specification.arrival_deadline
        == original_cargo.route_specification.arrival_deadline
    )


@pytest.mark.django_db
def test_deadline_dialog_updates_cargo_and_completes_htmx_dialog():
    call_command('seed_sample_data')
    _, deadline_view = build_dialog_views()
    cargo_repository = DjangoCargoRepository()
    original_cargo = cargo_repository.find(TrackingId('DEF789'))
    assert original_cargo is not None

    response = deadline_view(
        RequestFactory().post(
            '/admin/cargo/DEF789/deadline/',
            {'deadline': '2027-02-01'},
            HTTP_HX_REQUEST='true',
        ),
        'DEF789',
    )
    updated_cargo = cargo_repository.find(TrackingId('DEF789'))

    assert response.status_code == 204
    assert response['HX-Redirect'] == '/admin/dashboard/'
    assert response.content == b''
    assert updated_cargo is not None
    assert updated_cargo.route_specification.origin == original_cargo.route_specification.origin
    assert updated_cargo.route_specification.destination == (
        original_cargo.route_specification.destination
    )
    assert updated_cargo.route_specification.arrival_deadline.strftime('%Y-%m-%d') == '2027-02-01'


@pytest.mark.django_db
def test_dialog_for_unknown_cargo_returns_not_found():
    call_command('seed_sample_data')
    destination_view, _ = build_dialog_views()

    with pytest.raises(Http404, match='Cargo with tracking ID MISSING1 not found.'):
        destination_view(
            RequestFactory().get('/admin/cargo/MISSING1/destination/'),
            'MISSING1',
        )
