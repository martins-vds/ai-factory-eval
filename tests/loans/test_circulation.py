import re
from datetime import timedelta

import pytest
from django.test import Client
from django.utils import timezone
from playwright.sync_api import sync_playwright


@pytest.mark.django_db
def test_lend_endpoint_creates_a_loan_with_fourteen_day_due_date(client):
    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    today = timezone.localdate()
    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;dee;123;{today};{today + timedelta(days=14)};\n'
    )


@pytest.mark.django_db
def test_return_endpoint_records_today_and_returns_the_updated_loan(client):
    response = client.post('/loans/L1/return')

    today = timezone.localdate()
    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L1;ana;9780134685991;2026-01-02;2026-01-16;{today}\n'
    )


@pytest.mark.django_db
def test_repeat_return_is_rejected_without_replacing_the_original_date(client):
    response = client.post('/loans/L2/return')

    assert response.status_code == 409
    assert response.content.decode() == 'loan already returned\n'
    assert client.get('/loans/L2').content.decode() == (
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
    )


@pytest.mark.parametrize(
    'form_data',
    [
        {},
        {'member': 'dee'},
        {'isbn': '123'},
        {'member': '', 'isbn': '123'},
        {'member': '   ', 'isbn': '123'},
        {'member': 'dee', 'isbn': ''},
        {'member': 'dee', 'isbn': '   '},
    ],
)
@pytest.mark.django_db
def test_lend_endpoint_rejects_missing_or_blank_fields(client, form_data):
    response = client.post('/loans', form_data)

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'member and isbn are required\n'


@pytest.mark.django_db
def test_lend_endpoint_escapes_field_and_record_delimiters(client):
    response = client.post(
        '/loans',
        {'member': 'Reader; Example\nSecond line', 'isbn': '978"xyz'},
    )

    today = timezone.localdate()
    assert response.status_code == 201
    assert response.content.decode() == (
        f'L4;"Reader; Example\nSecond line";"978""xyz";'
        f'{today};{today + timedelta(days=14)};\n'
    )


@pytest.mark.django_db
def test_api_write_endpoints_accept_legacy_requests_without_csrf_tokens():
    api_client = Client(enforce_csrf_checks=True)

    lend_response = api_client.post('/loans', {'member': 'reader', 'isbn': '123'})
    return_response = api_client.post('/loans/L4/return')

    assert lend_response.status_code == 201
    assert return_response.status_code == 200
    assert return_response.content.decode().endswith(
        f'{timezone.localdate()}\n'
    )


@pytest.mark.django_db
def test_return_endpoint_reports_unknown_loan_in_the_characterized_format(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_new_loan_page_offers_the_reading_room_lend_form(client):
    response = client.get('/ui/loans/new/')

    assert response.status_code == 200
    assert b'Books in good company.' in response.content
    assert b'Lend a book' in response.content
    assert b'action="/ui/loans/"' in response.content
    assert b'hx-boost="true"' in response.content
    assert b'name="member"' in response.content
    assert b'name="isbn"' in response.content


@pytest.mark.django_db
def test_ui_lend_form_shows_field_errors_for_blank_values(client):
    response = client.post('/ui/loans/', {'member': '   ', 'isbn': ''})

    assert response.status_code == 200
    assert response.content.count(b'role="alert"') == 2
    assert b'This field is required.' in response.content
    assert b'Loan L4' not in response.content


@pytest.mark.django_db
def test_ui_lending_form_still_requires_a_csrf_token():
    response = Client(enforce_csrf_checks=True).post(
        '/ui/loans/',
        {'member': 'reader', 'isbn': '123'},
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_ui_lend_form_creates_a_loan_and_returns_to_the_collection(client):
    response = client.post('/ui/loans/', {'member': 'reader', 'isbn': '123'})

    assert response.status_code == 200
    assert b'Loan L4 created.' in response.content
    assert b'Loan L4' in response.content
    assert client.get('/loans/L4').content.decode().startswith('L4;reader;123;')


@pytest.mark.django_db
def test_ui_return_form_updates_the_collection(client):
    response = client.post('/ui/loans/L1/return/')

    assert response.status_code == 200
    assert b'Loan L1 returned.' in response.content
    assert b'Returned ' in response.content
    assert b'Return L1' not in response.content
    assert client.get('/loans/L1').content.decode().endswith(
        f'{timezone.localdate()}\n'
    )


@pytest.mark.django_db
def test_ui_rejects_repeated_returns_without_replacing_the_original_date(client):
    response = client.post('/ui/loans/L2/return/')

    assert response.status_code == 200
    assert b'role="alert"' in response.content
    assert b'original return date is unchanged' in response.content
    assert client.get('/loans/L2').content.decode().endswith('2026-01-20\n')


@pytest.mark.django_db
def test_browser_can_lend_and_return_from_the_reading_room(live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/loans/new/')
            page.get_by_label('Member name').fill('reader')
            page.get_by_label('ISBN').fill('123')
            page.get_by_role('button', name='Create 14-day loan').click()
            page.get_by_text('Loan L4 created.').wait_for()

            page.get_by_role('button', name='Return L1').click()
            page.get_by_text('Loan L1 returned.').wait_for()
            loan_row = page.locator('article').filter(has_text='Loan L1')
            assert loan_row.get_by_text(re.compile(r'^Returned .+')).is_visible()
        finally:
            browser.close()
