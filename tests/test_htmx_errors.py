from datetime import date, timedelta

import pytest
from django.core.management import call_command
from django.utils import timezone

RESPONSE_HANDLING = (
    b'"responseHandling":[{"code":"204","swap":false},{"code":"[23]..","swap":true},'
    b'{"code":"[45]..","swap":true,"error":true},{"code":"...","swap":true}]'
)


def _assert_page_handles_error_swaps(page, target, fragment=None):
    content = page.content
    target_content = (fragment or page).content
    target_id = target.removeprefix('#').encode()

    assert page.status_code == 200
    assert b'name="htmx-config"' in content
    assert RESPONSE_HANDLING in content
    assert f'hx-target="{target}"'.encode() in target_content
    assert b'id="' + target_id + b'"' in target_content


@pytest.mark.django_db
def test_live_map_page_swaps_failed_marker_response(client, monkeypatch):
    page = client.get('/admin/live-map/')

    def fail_map_fetch(*args, **kwargs):
        raise RuntimeError('map service unavailable')

    monkeypatch.setattr(
        'cargotracker.cargo.interfaces.admin_map.views.build_admin_map_data',
        fail_map_fetch,
    )
    client.raise_request_exception = False
    response = client.get('/admin/live-map/markers/', HTTP_HX_REQUEST='true')

    assert response.status_code == 500
    assert response.content
    _assert_page_handles_error_swaps(page, '#live-map-markers')


@pytest.mark.django_db
def test_not_routed_table_page_swaps_unknown_cargo_response(client):
    call_command('seed_sample_data')
    page = client.get('/admin/dashboard/')
    response = client.get(
        '/admin/cargo/UNKNOWN/destination/',
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 404
    assert response.content
    _assert_page_handles_error_swaps(page, '#cargo-edit-dialog-content')


@pytest.mark.django_db
def test_deadline_dialog_page_swaps_invalid_deadline_error(client):
    call_command('seed_sample_data')
    page = client.get('/admin/dashboard/')
    response = client.post(
        '/admin/cargo/DEF789/deadline/',
        {'deadline': 'not-a-date'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert b'Enter a valid arrival deadline.' in response.content
    _assert_page_handles_error_swaps(page, '#cargo-edit-dialog-content')


@pytest.mark.django_db
def test_destination_dialog_page_swaps_invalid_destination_error(client):
    call_command('seed_sample_data')
    page = client.get('/admin/dashboard/')
    response = client.post(
        '/admin/cargo/DEF789/destination/',
        {'destination': 'UNKNOWN'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert b'Select a valid destination.' in response.content
    _assert_page_handles_error_swaps(page, '#cargo-edit-dialog-content')


@pytest.mark.django_db
def test_booking_deadline_form_swaps_expired_deadline_error(client, monkeypatch):
    call_command('seed_sample_data')
    page = client.get('/booking/')
    today = date(2026, 11, 18)
    monkeypatch.setattr(timezone, 'localdate', lambda: today)
    response = client.post(
        '/booking/',
        {
            'step': 'deadline',
            'origin': 'USCHI',
            'destination': 'USDAL',
            'deadline': (today - timedelta(days=1)).isoformat(),
        },
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert b'Arrival deadline cannot be before today.' in response.content
    _assert_page_handles_error_swaps(page, '#deadline-form', response)


@pytest.mark.django_db
def test_tracking_page_swaps_unknown_tracking_id_error(client):
    page = client.get('/')
    response = client.post(
        '/',
        {'tracking_id': 'UNKNOWN'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert b'Cargo with tracking ID UNKNOWN not found.' in response.content
    _assert_page_handles_error_swaps(page, '#tracking-result')
