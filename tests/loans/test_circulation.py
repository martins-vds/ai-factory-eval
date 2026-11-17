from datetime import timedelta

import pytest
from django.utils import timezone
from playwright.sync_api import sync_playwright


@pytest.mark.django_db
def test_lending_endpoint_creates_a_loan_with_fourteen_day_due_date(client):
    today = timezone.localdate()
    due_on = today + timedelta(days=14)

    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == f'L4;dee;123;{today};{due_on};\n'
    assert client.get('/loans/L4').content.decode() == (f'L4;dee;123;{today};{due_on};\n')


@pytest.mark.django_db
def test_return_endpoint_records_today_and_returns_the_updated_loan(client):
    today = timezone.localdate()

    response = client.post('/loans/L1/return')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (f'L1;ana;9780134685991;2026-01-02;2026-01-16;{today}\n')
    assert client.get('/loans/L1').content.decode() == (
        f'L1;ana;9780134685991;2026-01-02;2026-01-16;{today}\n'
    )


@pytest.mark.django_db
def test_repeat_return_is_rejected_without_changing_the_original_date(client):
    response = client.post('/loans/L2/return')

    assert response.status_code == 409
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'loan already returned\n'
    assert client.get('/loans/L2').content.decode() == (
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
    )


@pytest.mark.django_db
def test_browser_can_lend_a_book_from_the_reading_room_form(client):
    page = client.get('/ui/loans/new/')

    assert page.status_code == 200
    assert b'Lend a book' in page.content

    response = client.post('/ui/loans/new/', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/'
    catalog = client.get(response['Location'])
    assert b'Loan L4' in catalog.content
    assert b'dee' in catalog.content


@pytest.mark.django_db
def test_htmx_lending_redirects_to_the_catalog(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': 'dee', 'isbn': '123'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 204
    assert response['HX-Redirect'] == '/ui/loans/'


@pytest.mark.django_db
def test_lending_api_rejects_missing_and_blank_values(client):
    invalid_forms = (
        {},
        {'member': 'dee'},
        {'isbn': '123'},
        {'member': ' ', 'isbn': '123'},
        {'member': 'dee', 'isbn': '  '},
    )

    for form in invalid_forms:
        response = client.post('/loans', form)

        assert response.status_code == 400
        assert response.content.decode() == 'member and isbn are required\n'

    assert len(client.get('/loans').content.decode().splitlines()) == 3


@pytest.mark.django_db
def test_browser_lending_displays_field_errors_for_blank_values(client):
    response = client.post('/ui/loans/new/', {'member': ' ', 'isbn': ''})

    assert response.status_code == 400
    assert b'This field is required.' in response.content
    assert response.context['form'].errors.keys() == {'member', 'isbn'}
    assert len(client.get('/loans').content.decode().splitlines()) == 3


@pytest.mark.django_db
def test_browser_lending_displays_errors_when_no_fields_are_submitted(client):
    response = client.post('/ui/loans/new/')

    assert response.status_code == 400
    assert response.context['form'].errors.keys() == {'member', 'isbn'}
    assert response.content.count(b'This field is required.') == 2


@pytest.mark.django_db
def test_browser_can_return_an_unreturned_book(client):
    response = client.post('/ui/loans/L1/return/')

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/L1/'
    detail = client.get(response['Location'])
    assert b'Returned' in detail.content
    assert b'Record return' not in detail.content


@pytest.mark.django_db
def test_htmx_return_redirects_to_the_updated_loan(client):
    response = client.post(
        '/ui/loans/L1/return/',
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 204
    assert response['HX-Redirect'] == '/ui/loans/L1/'


@pytest.mark.django_db
def test_return_api_returns_not_found_for_an_unknown_loan(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_browser_repeat_return_shows_error_without_overwriting_date(client):
    response = client.post('/ui/loans/L2/return/')

    assert response.status_code == 409
    assert b'This book has already been returned.' in response.content
    assert b'Jan 20, 2026' in response.content
    assert b'Record return' not in response.content


@pytest.mark.django_db
def test_browser_can_lend_and_return_a_book(client, live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/loans/')
            page.get_by_role('link', name='Lend a book').click()
            page.get_by_label('Member').fill('reader')
            page.get_by_label('ISBN').fill('123')
            page.get_by_role('button', name='Record this loan').click()
            page.wait_for_url(f'{live_server.url}/ui/loans/')
            assert page.get_by_text('reader · ISBN 123').is_visible()

            page.get_by_role('link', name='Loan L4').click()
            page.get_by_role('button', name='Record return').click()
            page.wait_for_url(f'{live_server.url}/ui/loans/L4/')
            assert page.get_by_text('Returned', exact=True).is_visible()
            assert page.get_by_role('button', name='Record return').count() == 0
        finally:
            browser.close()
