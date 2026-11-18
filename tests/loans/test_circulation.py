from datetime import timedelta

import pytest
from django.utils import timezone
from playwright.sync_api import sync_playwright


@pytest.mark.django_db
def test_api_lending_creates_a_loan_with_a_fourteen_day_due_date(client):
    lent_on = timezone.localdate()

    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;dee;123;{lent_on.isoformat()};{(lent_on + timedelta(days=14)).isoformat()};\n'
    )


@pytest.mark.django_db
def test_api_return_records_today_and_persists_the_return_date(client):
    returned_on = timezone.localdate()

    response = client.post('/loans/L1/return')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L1;ana;9780134685991;2026-01-02;2026-01-16;{returned_on.isoformat()}\n'
    )
    assert client.get('/loans/L1').content == response.content


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('payload', 'field'),
    [
        ({}, 'member'),
        ({'member': 'dee'}, 'isbn'),
        ({'member': '', 'isbn': '123'}, 'member'),
        ({'member': 'dee', 'isbn': ''}, 'isbn'),
        ({'member': ' ', 'isbn': '123'}, 'member'),
        ({'member': 'dee', 'isbn': ' '}, 'isbn'),
    ],
)
def test_api_lending_rejects_missing_or_blank_fields(client, payload, field):
    response = client.post('/loans', payload)

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert field.encode() in response.content
    assert client.get('/loans').content.decode().count('\n') == 3


@pytest.mark.django_db
def test_api_lending_returns_field_errors_for_missing_values(client):
    response = client.post('/loans', {})

    assert response.status_code == 400
    assert response.content.decode() == (
        'member: This field is required.\nisbn: This field is required.'
    )


@pytest.mark.django_db
def test_api_lending_escapes_delimiters_and_quotes_in_fields(client):
    lent_on = timezone.localdate()
    due_on = lent_on + timedelta(days=14)

    response = client.post('/loans', {'member': 'reader; one', 'isbn': '978"abc'})

    assert response.status_code == 201
    assert response.content.decode() == (
        f'L4;"reader; one";"978""abc";{lent_on.isoformat()};{due_on.isoformat()};\n'
    )


@pytest.mark.django_db
def test_api_repeated_return_is_rejected_without_replacing_the_original_date(client):
    response = client.post('/loans/L2/return')

    assert response.status_code == 409
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'already returned\n'
    assert client.get('/loans/L2').content == (
        b'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
    )


@pytest.mark.django_db
def test_api_return_of_unknown_loan_is_not_found(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'no such loan\n'


@pytest.mark.django_db
def test_browser_can_lend_a_book_from_the_reading_room_page(client):
    lent_on = timezone.localdate()
    list_response = client.get('/ui/loans/')
    form_response = client.get('/ui/loans/new/')

    assert b'href="/ui/loans/new/"' in list_response.content
    assert form_response.status_code == 200
    assert b'Lend a book' in form_response.content
    assert b'name="member"' in form_response.content
    assert b'name="isbn"' in form_response.content

    response = client.post('/ui/loans/new/', {'member': 'reader', 'isbn': '123'})

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/L4/'
    loan_detail = client.get(response['Location'])
    assert b'reader' in loan_detail.content
    assert lent_on.strftime('%b %-d, %Y').encode() in loan_detail.content


@pytest.mark.django_db
def test_browser_lending_page_shows_full_page_errors_for_blank_fields(client):
    response = client.post('/ui/loans/new/', {})

    assert response.status_code == 200
    assert b'<!doctype html>' in response.content
    assert response.content.count(b'This field is required.') == 2
    assert response.content.count(b'role="alert"') == 2
    assert client.get('/loans').content.decode().count('\n') == 3


@pytest.mark.django_db
def test_browser_can_lend_a_book_with_htmx(client):
    form_response = client.get('/ui/loans/new/')

    assert b'hx-post="/ui/loans/new/"' in form_response.content

    response = client.post(
        '/ui/loans/new/',
        {'member': 'reader', 'isbn': '123'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert b'Loan L4 is ready.' in response.content
    assert b'href="/ui/loans/L4/"' in response.content
    assert client.get('/loans/L4').status_code == 200


@pytest.mark.django_db
def test_htmx_lending_errors_replace_only_the_form(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': '', 'isbn': ''},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert b'<!doctype html>' not in response.content
    assert b'id="loan-form"' in response.content
    assert response.content.count(b'This field is required.') == 2
    assert client.get('/loans').content.decode().count('\n') == 3


@pytest.mark.django_db
def test_browser_can_return_a_loan_with_htmx(client):
    returned_on = timezone.localdate()
    detail = client.get('/ui/loans/L1/')

    assert b'hx-post="/ui/loans/L1/return/"' in detail.content

    response = client.post('/ui/loans/L1/return/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert f'Returned on {returned_on.isoformat()}'.encode() in response.content
    assert returned_on.isoformat().encode() in client.get('/loans/L1').content


@pytest.mark.django_db
def test_browser_regular_return_redirects_to_the_updated_loan(client):
    response = client.post('/ui/loans/L1/return/')

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/L1/'
    assert b'Returned on' in client.get(response['Location']).content


@pytest.mark.django_db
def test_browser_repeated_htmx_return_keeps_original_date(client):
    response = client.post('/ui/loans/L2/return/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="alert"' in response.content
    assert b'already returned on 2026-01-20' in response.content
    assert b'2026-01-20' in client.get('/loans/L2').content


@pytest.mark.django_db
def test_browser_regular_repeated_return_shows_original_record_and_date(client):
    response = client.post('/ui/loans/L2/return/')

    assert response.status_code == 409
    assert b'role="alert"' in response.content
    assert b'already been returned' in response.content
    assert b'Loan record \xc2\xb7 L2' in response.content
    assert b'Jan 20, 2026' in response.content
    assert b'2026-01-20' in client.get('/loans/L2').content


@pytest.mark.django_db
def test_browser_return_of_unknown_loan_is_not_found(client):
    response = client.post('/ui/loans/unknown/return/')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'no such loan\n'


@pytest.mark.django_db
def test_real_browser_can_lend_and_return_a_book(live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/loans/new/')
            htmx_available = page.evaluate("typeof window.htmx !== 'undefined'")
            page.get_by_label('Member').fill('reader')
            page.get_by_label('ISBN').fill('123')
            page.get_by_role('button', name='Lend book').click()

            if htmx_available:
                status = page.get_by_role('status')
                status.wait_for()
                assert status.inner_text().startswith('Loan L4 is ready.')
                page.get_by_role('link', name='View loan').click()
            else:
                page.wait_for_url('**/ui/loans/L4/')

            page.get_by_role('button', name='Return book').click()
            page.locator('#return-status').wait_for()
            returned_on = timezone.localdate().isoformat()
            assert page.locator('#return-status').inner_text() == f'Returned on {returned_on}'
        finally:
            browser.close()


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('path', 'method'),
    [
        ('/loans', 'put'),
        ('/loans/L1/return', 'get'),
        ('/ui/loans/new/', 'put'),
        ('/ui/loans/L1/return/', 'get'),
    ],
)
def test_loan_write_routes_reject_unsupported_methods(client, path, method):
    response = getattr(client, method)(path)

    assert response.status_code == 405
    assert client.get('/loans/L1').content.endswith(b';\n')
