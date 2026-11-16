from datetime import date

import pytest
from django.utils import timezone


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
        key: value
        for key, value in {'member': member, 'isbn': isbn}.items()
        if value is not None
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
    assert response.content.decode() == (
        'L4;reader;9780134685991;2026-03-01;2026-03-15;\n'
    )
    assert client.get('/loans/L4').content.decode() == (
        'L4;reader;9780134685991;2026-03-01;2026-03-15;\n'
    )


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
