from datetime import date

import pytest
from django.utils import timezone


@pytest.mark.django_db
def test_lending_creates_a_14_day_loan(client, monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 3, 1))

    response = client.post('/loans', {'member': ' reader ', 'isbn': ' 123 '})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'L4; reader ; 123 ;2026-03-01;2026-03-15;\n'

    saved_loan = client.get('/loans/L4')
    assert saved_loan.status_code == 200
    assert saved_loan.content.decode() == 'L4; reader ; 123 ;2026-03-01;2026-03-15;\n'


@pytest.mark.parametrize(
    ('data', 'body'),
    [
        ({'isbn': '123'}, 'member and isbn are required\n'),
        ({'member': 'reader'}, 'member and isbn are required\n'),
        (
            {'member': ' ', 'isbn': '123'},
            'member: This field is required.\n',
        ),
        (
            {'member': 'reader', 'isbn': ' '},
            'isbn: This field is required.\n',
        ),
        (
            {'member': 'reader', 'isbn': ''},
            'isbn: This field is required.\n',
        ),
    ],
)
@pytest.mark.django_db
def test_lending_requires_member_and_isbn(client, data, body):
    response = client.post('/loans', data)

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == body
    assert client.get('/loans/L4').status_code == 404


@pytest.mark.django_db
def test_return_records_the_date_and_returns_the_updated_loan(client, monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 3, 1))

    response = client.post('/loans/L1/return')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == ('L1;ana;9780134685991;2026-01-02;2026-01-16;2026-03-01\n')


@pytest.mark.django_db
def test_repeated_return_is_rejected_without_changing_the_return_date(client, monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 3, 1))
    client.post('/loans/L1/return')
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 3, 2))

    response = client.post('/loans/L1/return')

    assert response.status_code == 409
    assert response.content.decode() == 'loan already returned\n'
    saved_loan = client.get('/loans/L1')
    assert saved_loan.content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;2026-03-01\n'
    )


@pytest.mark.django_db
def test_return_of_unknown_loan_preserves_the_characterized_not_found_response(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_browser_can_lend_a_book_from_the_reading_room_form(client, monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 3, 1))

    form_page = client.get('/ui/loans/new/')

    assert form_page.status_code == 200
    assert b'Lend a book' in form_page.content
    assert b'name="member"' in form_page.content
    assert b'name="isbn"' in form_page.content

    response = client.post('/ui/loans/new/', {'member': 'reader', 'isbn': '123'})

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/'
    saved_loan = client.get('/loans/L4')
    assert saved_loan.content.decode() == 'L4;reader;123;2026-03-01;2026-03-15;\n'


@pytest.mark.django_db
@pytest.mark.parametrize('data', [{'member': ' ', 'isbn': ''}, {}])
def test_browser_lending_shows_field_errors_for_blank_values(client, data):
    response = client.post('/ui/loans/new/', data)

    assert response.status_code == 400
    assert b'Member name' in response.content
    assert b'ISBN' in response.content
    assert response.content.count(b'This field is required.') == 2
    assert client.get('/loans/L4').status_code == 404


@pytest.mark.django_db
def test_htmx_lending_displays_field_errors_for_blank_values(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': ' ', 'isbn': '123'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert b'Member name' in response.content
    assert b'This field is required.' in response.content
    assert client.get('/loans/L4').status_code == 404


@pytest.mark.django_db
def test_browser_can_return_a_loan_without_overwriting_its_return_date(client, monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 3, 1))

    catalog = client.get('/ui/loans/')
    assert catalog.status_code == 200
    assert b'Return L1' in catalog.content

    response = client.post('/ui/loans/L1/return/')

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/'
    saved_loan = client.get('/loans/L1')
    expected_loan = 'L1;ana;9780134685991;2026-01-02;2026-01-16;2026-03-01\n'
    assert saved_loan.content.decode() == expected_loan

    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 3, 2))
    repeated = client.post('/ui/loans/L1/return/', HTTP_HX_REQUEST='true')

    assert repeated.status_code == 200
    assert b'This loan has already been returned.' in repeated.content
    assert b'Return L1' not in repeated.content
    assert client.get('/loans/L1').content.decode() == expected_loan
