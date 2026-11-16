import json
from datetime import date
from pathlib import Path

import pytest
from django.utils import timezone
from playwright.sync_api import sync_playwright


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('member', 'isbn'),
    [
        (None, '9780134685991'),
        ('reader', None),
        ('', '9780134685991'),
        ('   ', '9780134685991'),
        ('reader', ''),
        ('reader', '   '),
    ],
)
def test_lend_api_rejects_blank_member_and_isbn(client, member, isbn):
    data = {
        key: value for key, value in {'member': member, 'isbn': isbn}.items() if value is not None
    }
    response = client.post('/loans', data)

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'member and isbn are required\n'


@pytest.mark.django_db
def test_lend_api_creates_loan_with_fourteen_day_due_date(client, monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 3, 1))

    response = client.post(
        '/loans',
        {'member': 'reader', 'isbn': '9780134685991'},
    )

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == ('L4;reader;9780134685991;2026-03-01;2026-03-15;\n')
    assert client.get('/loans/L4').content.decode() == (
        'L4;reader;9780134685991;2026-03-01;2026-03-15;\n'
    )


@pytest.mark.django_db
def test_lend_api_preserves_surrounding_whitespace(client, monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 3, 1))

    response = client.post(
        '/loans',
        {'member': '  reader  ', 'isbn': '  123  '},
    )

    assert response.status_code == 201
    assert response.content.decode() == 'L4;  reader  ;  123  ;2026-03-01;2026-03-15;\n'


@pytest.mark.django_db
def test_return_api_persists_date_and_rejects_a_repeat(client, monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 3, 1))

    first_return = client.post('/loans/L1/return')

    assert first_return.status_code == 200
    assert first_return['Content-Type'] == 'text/plain'
    assert first_return.content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;2026-03-01\n'
    )

    repeated_return = client.post('/loans/L1/return')

    assert repeated_return.status_code == 409
    assert repeated_return['Content-Type'] == 'text/plain'
    assert repeated_return.content.decode() == 'loan already returned\n'

    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 3, 2))
    later_return = client.post('/loans/L1/return')
    assert later_return.status_code == 409

    assert client.get('/loans/L1').content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;2026-03-01\n'
    )

    missing_loan = client.post('/loans/unknown/return')
    assert missing_loan.status_code == 404
    assert missing_loan.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_new_loan_page_uses_reading_room_layout_and_exposes_lend_form(client):
    response = client.get('/ui/loans/new/')

    assert response.status_code == 200
    assert b'A book belongs in a good story.' in response.content
    assert b'name="member"' in response.content
    assert b'name="isbn"' in response.content
    assert b'htmx.org@2.0.11' in response.content
    assert b'<span class="label-text">Member</span>' in response.content
    assert b'<span class="label-text">ISBN</span>' in response.content
    assert b'class="input input-bordered w-full"' in response.content


@pytest.mark.django_db
def test_loan_list_offers_lending_and_active_loan_return_controls(client):
    response = client.get('/ui/loans/')

    assert response.status_code == 200
    assert b'href="/ui/loans/new/"' in response.content
    assert b'hx-post="/ui/loans/L1/return/"' in response.content
    assert b'hx-post="/ui/loans/L2/return/"' not in response.content


@pytest.mark.django_db
def test_lend_form_reports_blank_field_errors(client):
    response = client.post('/ui/loans/new/', {'member': '   ', 'isbn': ''})

    assert response.status_code == 200
    assert b'Enter a member.' in response.content
    assert b'Enter an ISBN.' in response.content

    missing_member = client.post('/ui/loans/new/', {'isbn': '9780134685991'})
    assert b'Enter a member.' in missing_member.content

    missing_isbn = client.post('/ui/loans/new/', {'member': 'reader'})
    assert b'Enter an ISBN.' in missing_isbn.content

    too_long = client.post(
        '/ui/loans/new/',
        {'member': 'm' * 256, 'isbn': 'i' * 256},
    )
    assert b'Ensure this value has at most 255 characters' in too_long.content


@pytest.mark.django_db
def test_lend_form_redirects_to_collection_after_creating_loan(client, monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 3, 1))

    response = client.post(
        '/ui/loans/new/',
        {'member': 'reader', 'isbn': '9780134685991'},
    )

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/'
    collection = client.get(response['Location'])
    assert b'Loan L4' in collection.content
    assert b'ISBN 9780134685991' in collection.content


@pytest.mark.django_db
def test_htmx_return_updates_row_and_rejects_repeated_return(client, monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 3, 1))

    response = client.post(
        '/ui/loans/L1/return/',
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert b'Returned Mar 1, 2026' in response.content
    assert b'hx-post=' not in response.content

    repeated = client.post('/ui/loans/L1/return/', HTTP_HX_REQUEST='true')
    assert repeated.status_code == 200
    assert b'This book has already been returned.' in repeated.content

    assert client.get('/loans/L1').content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;2026-03-01\n'
    )


@pytest.mark.django_db
def test_return_routes_reject_unsupported_methods_and_unknown_loans(client):
    assert client.get('/loans/L1/return').status_code == 405
    assert client.get('/ui/loans/L1/return/').status_code == 405

    missing = client.post('/ui/loans/unknown/return/')
    assert missing.status_code == 404
    assert missing.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_non_htmx_return_redirects_and_shows_repeat_error(client, monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 3, 1))

    returned = client.post('/ui/loans/L1/return/')
    assert returned.status_code == 302
    assert returned['Location'] == '/ui/loans/'

    repeated = client.post('/ui/loans/L1/return/')
    assert repeated.status_code == 409
    assert b'This book has already been returned.' in repeated.content


@pytest.mark.django_db
def test_lend_and_return_match_characterized_source_http_goldens(client, monkeypatch):
    goldens_path = Path('.migration/characterization/source/goldens/http.json')
    goldens = json.loads(goldens_path.read_text())

    for case, path in (('GET /loans', '/loans'), ('GET /loans/{id}', '/loans/L1')):
        expected = goldens[case]['response']
        actual = client.get(path)
        assert actual.status_code == expected['status']
        assert actual['Content-Type'] == expected['content_type']
        assert actual.content.decode() == expected['body']

    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 11, 8))
    expected_lend = goldens['POST /loans']['response']
    lend = client.post('/loans', {'member': 'dee', 'isbn': '123'})
    assert lend.status_code == expected_lend['status']
    assert lend['Content-Type'] == expected_lend['content_type']
    assert lend.content.decode() == expected_lend['body']

    expected_return = goldens['POST /loans/{id}/return']['response']
    returned = client.post('/loans/L1/return')
    assert returned.status_code == expected_return['status']
    assert returned['Content-Type'] == expected_return['content_type']
    assert returned.content.decode() == expected_return['body']


@pytest.mark.django_db
def test_browser_can_lend_and_return_a_book(live_server, monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 3, 1))

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/loans/')
            page.get_by_role('link', name='Lend a book').click()
            page.get_by_label('Member').fill('reader')
            page.get_by_label('ISBN').fill('9780134685991')
            page.get_by_role('button', name='Lend this book').click()

            loan_row = page.locator('#loan-L4')
            assert loan_row.is_visible()
            loan_row.get_by_role('button', name='Mark returned').click()
            loan_row.get_by_text('Returned Mar 1, 2026').wait_for()
            assert loan_row.get_by_role('button', name='Mark returned').count() == 0
        finally:
            browser.close()
