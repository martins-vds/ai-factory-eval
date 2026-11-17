from datetime import timedelta

import pytest
from django.utils import timezone


@pytest.mark.parametrize(
    'fields',
    [
        {'isbn': '123'},
        {'member': 'reader'},
        {'member': '', 'isbn': '123'},
        {'member': 'reader', 'isbn': ''},
        {'member': ' \t ', 'isbn': '123'},
        {'member': 'reader', 'isbn': ' \t '},
    ],
)
@pytest.mark.django_db
def test_lending_endpoint_rejects_missing_and_blank_fields(client, fields):
    response = client.post('/loans', fields)

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'member and isbn are required\n'


@pytest.mark.django_db
def test_lending_endpoint_creates_a_loan_with_fourteen_day_due_date(client):
    lent_on = timezone.localdate()

    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;dee;123;{lent_on.isoformat()};{(lent_on + timedelta(days=14)).isoformat()};\n'
    )
    assert client.get('/loans/L4').content == response.content


@pytest.mark.django_db
def test_lending_endpoint_escapes_delimiters_in_the_export(client):
    lent_on = timezone.localdate()

    response = client.post('/loans', {'member': 'a;b', 'isbn': '123;456'})

    assert response.status_code == 201
    assert response.content.decode() == (
        f'L4;"a;b";"123;456";{lent_on.isoformat()};'
        f'{(lent_on + timedelta(days=14)).isoformat()};\n'
    )


@pytest.mark.django_db
def test_return_endpoint_rejects_repeated_returns_without_replacing_the_date(client):
    returned_on = timezone.localdate()

    response = client.post('/loans/L1/return')

    assert response.status_code == 200
    expected_record = (
        f'L1;ana;9780134685991;2026-01-02;2026-01-16;{returned_on.isoformat()}\n'
    )
    assert response.content.decode() == expected_record

    repeated = client.post('/loans/L1/return')

    assert repeated.status_code == 409
    assert repeated.content.decode() == 'loan has already been returned\n'
    assert client.get('/loans/L1').content.decode() == expected_record


@pytest.mark.django_db
def test_return_endpoint_preserves_an_existing_return_date(client):
    response = client.post('/loans/L2/return')

    assert response.status_code == 409
    assert response.content.decode() == 'loan has already been returned\n'
    assert client.get('/loans/L2').content.decode() == (
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
    )


@pytest.mark.django_db
def test_return_endpoint_returns_not_found_for_unknown_loan(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_browser_lending_page_uses_the_reading_room_htmx_form(client):
    response = client.get('/ui/loans/new/')

    assert response.status_code == 200
    assert b'Lend a book' in response.content
    assert b'name="member"' in response.content
    assert b'name="isbn"' in response.content
    assert b'hx-post="/ui/loans/new/"' in response.content


@pytest.mark.django_db
def test_browser_lending_form_shows_field_errors_for_blank_values(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': ' \t ', 'isbn': ''},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert b'Member: This field is required.' in response.content
    assert b'ISBN: This field is required.' in response.content
    assert b'<!doctype html>' not in response.content


@pytest.mark.django_db
def test_browser_lending_form_returns_htmx_success_for_a_new_loan(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': 'dee', 'isbn': '123'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert b'Loan L4 is now in the collection.' in response.content
    assert b'role="status"' in response.content


@pytest.mark.django_db
def test_browser_return_uses_htmx_and_keeps_the_first_return_date(client):
    detail = client.get('/ui/loans/L1/')

    assert detail.status_code == 200
    assert b'hx-post="/ui/loans/L1/return/"' in detail.content

    response = client.post('/ui/loans/L1/return/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="status"' in response.content
    assert b'Returned' in response.content

    repeated = client.post('/ui/loans/L1/return/', HTTP_HX_REQUEST='true')

    assert repeated.status_code == 200
    assert b'role="alert"' in repeated.content
    assert b'already been returned' in repeated.content
    assert client.get('/loans/L1').content.decode().endswith(
        f'{timezone.localdate().isoformat()}\n'
    )

    existing = client.post('/ui/loans/L2/return/', HTTP_HX_REQUEST='true')

    assert existing.status_code == 200
    assert b'already been returned' in existing.content
    assert b'Returned Jan 20, 2026' in existing.content
    assert client.get('/loans/L2').content.decode().endswith('2026-01-20\n')
