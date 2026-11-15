import csv
from datetime import timedelta
from io import StringIO

import pytest
from django.utils import timezone

from src.loans.models import Loan


@pytest.mark.django_db
def test_lending_creates_a_formatted_loan_with_escaped_fields(client):
    member = 'Reader; Example\nSecond line'
    isbn = '978"xyz'
    today = timezone.localdate()

    response = client.post('/loans', {'member': member, 'isbn': isbn})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert next(csv.reader(StringIO(response.content.decode()), delimiter=';')) == [
        'L4',
        member,
        isbn,
        today.isoformat(),
        (today + timedelta(days=14)).isoformat(),
        '',
    ]


@pytest.mark.django_db
@pytest.mark.parametrize(
    'fields',
    [
        {'isbn': '123'},
        {'member': 'reader'},
        {'member': '', 'isbn': '123'},
        {'member': 'reader', 'isbn': ' \t '},
    ],
)
def test_lending_rejects_missing_and_blank_fields(client, fields):
    response = client.post('/loans', fields)

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'member and isbn are required\n'
    assert Loan.objects.count() == 3


@pytest.mark.django_db
def test_return_updates_a_loan_and_rejects_repeated_returns(client):
    today = timezone.localdate()

    first_response = client.post('/loans/L1/return')

    assert first_response.status_code == 200
    assert first_response['Content-Type'] == 'text/plain'
    assert first_response.content.decode() == (
        f'L1;ana;9780134685991;2026-01-02;2026-01-16;{today.isoformat()}\n'
    )

    repeated_response = client.post('/loans/L1/return')

    assert repeated_response.status_code == 409
    assert repeated_response['Content-Type'] == 'text/plain'
    assert repeated_response.content.decode() == 'loan already returned\n'
    assert Loan.objects.get(pk='L1').returned_on == today


@pytest.mark.django_db
def test_return_unknown_loan_returns_not_found(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_reading_room_can_lend_and_return_with_htmx(client):
    form_page = client.get('/ui/loans/new/')

    assert form_page.status_code == 200
    assert b'hx-post="/ui/loans/new/"' in form_page.content

    invalid_response = client.post(
        '/ui/loans/new/',
        {'member': ' \t ', 'isbn': ''},
        HTTP_HX_REQUEST='true',
    )

    assert invalid_response.status_code == 200
    assert b'Enter a member name; blank values are not accepted.' in invalid_response.content
    assert b'Enter an ISBN; blank values are not accepted.' in invalid_response.content
    assert Loan.objects.count() == 3

    lend_response = client.post(
        '/ui/loans/new/',
        {'member': 'reader', 'isbn': '123'},
        HTTP_HX_REQUEST='true',
    )

    assert lend_response.status_code == 204
    assert lend_response['HX-Redirect'] == '/ui/loans/'
    assert Loan.objects.get(pk='L4').member == 'reader'

    return_response = client.post(
        '/ui/loans/L1/return/',
        HTTP_HX_REQUEST='true',
    )

    assert return_response.status_code == 200
    assert b'Returned' in return_response.content
    assert b'hx-post="/ui/loans/L1/return/"' not in return_response.content
