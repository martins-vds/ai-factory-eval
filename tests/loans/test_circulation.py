from datetime import date, timedelta

import pytest
from django.utils import timezone
from playwright.sync_api import sync_playwright


@pytest.mark.django_db
def test_lending_creates_due_dated_loan_and_returns_formatted_record(client):
    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    fields = response.content.decode().strip().split(';')
    assert fields[:3] == ['L4', 'dee', '123']
    lent_on = date.fromisoformat(fields[3])
    assert lent_on == timezone.localdate()
    assert date.fromisoformat(fields[4]) == lent_on + timedelta(days=14)
    assert fields[5] == ''
    assert client.get('/loans/L4').content.decode() == response.content.decode()


@pytest.mark.django_db
def test_lending_escapes_delimiters_in_export_fields(client):
    response = client.post(
        '/loans',
        {'member': 'reader; guest', 'isbn': '123;456'},
    )
    lent_on = timezone.localdate()

    assert response.status_code == 201
    assert response.content.decode() == (
        f'L4;"reader; guest";"123;456";{lent_on.isoformat()};'
        f'{(lent_on + timedelta(days=14)).isoformat()};\n'
    )


@pytest.mark.parametrize(
    'form_data',
    [
        {'isbn': '123'},
        {'member': 'reader'},
        {'member': '', 'isbn': '123'},
        {'member': 'reader', 'isbn': ''},
        {'member': '   ', 'isbn': '123'},
        {'member': 'reader', 'isbn': '   '},
    ],
)
@pytest.mark.django_db
def test_lending_rejects_missing_or_blank_required_fields(client, form_data):
    response = client.post('/loans', form_data)

    assert response.status_code == 400
    assert response.content.decode() == 'member and isbn are required\n'
    assert client.get('/loans').content.decode().count('\n') == 3


@pytest.mark.django_db
def test_reading_room_has_a_loan_form(client):
    response = client.get('/ui/loans/new/')

    assert response.status_code == 200
    assert b'Lend a book' in response.content
    assert b'name="member"' in response.content
    assert b'name="isbn"' in response.content


@pytest.mark.django_db
def test_htmx_lending_creates_a_loan_and_returns_form_feedback(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': 'reader', 'isbn': '123'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 201
    assert b'Loan L4 created.' in response.content
    assert client.get('/loans/L4').content.decode().startswith('L4;reader;123;')


@pytest.mark.django_db
def test_htmx_lending_shows_field_errors_for_blank_values(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': '   ', 'isbn': ''},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 400
    assert response.content.decode().count('This field is required.') == 2
    assert client.get('/loans').content.decode().count('\n') == 3


@pytest.mark.django_db
def test_browser_can_lend_and_return_a_book(live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/loans/')
            page.get_by_role('link', name='Lend a book').click()
            page.get_by_label('Member').fill('reader')
            page.get_by_label('ISBN').fill('123')
            page.get_by_role('button', name='Lend book').click()
            page.wait_for_function(
                "() => location.pathname.endsWith('/ui/loans/L4/') || "
                "document.body.innerText.includes('Loan L4 created.')"
            )

            page.goto(f'{live_server.url}/ui/loans/L4/')
            page.get_by_role('button', name='Mark returned').click()
            page.wait_for_function("() => !document.body.innerText.includes('Mark returned')")
        finally:
            browser.close()


@pytest.mark.django_db
def test_reading_room_detail_offers_a_return_action(client):
    response = client.get('/ui/loans/L1/')

    assert response.status_code == 200
    assert b'Mark returned' in response.content
    assert b'hx-post="/ui/loans/L1/return/"' in response.content


@pytest.mark.django_db
def test_htmx_return_records_the_date_and_removes_the_action(client):
    response = client.post('/ui/loans/L1/return/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'Returned' in response.content
    assert b'Mark returned' not in response.content
    assert client.get('/loans/L1').content.decode().endswith(
        f'{timezone.localdate().isoformat()}\n'
    )


@pytest.mark.django_db
def test_returning_a_loan_sets_and_persists_return_date(client):
    response = client.post('/loans/L1/return')

    assert response.status_code == 200
    fields = response.content.decode().strip().split(';')
    assert fields[:5] == ['L1', 'ana', '9780134685991', '2026-01-02', '2026-01-16']
    assert fields[5] == timezone.localdate().isoformat()
    assert client.get('/loans/L1').content.decode() == response.content.decode()


@pytest.mark.django_db
def test_returning_an_unknown_loan_returns_the_characterized_not_found_response(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_repeated_return_is_rejected_without_replacing_the_return_date(client):
    response = client.post('/loans/L2/return')

    assert response.status_code == 409
    assert response.content.decode() == 'loan already returned\n'
    assert client.get('/loans/L2').content.decode() == (
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
    )
