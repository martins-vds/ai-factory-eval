import csv
from datetime import timedelta
from io import StringIO

import pytest
from django.utils import timezone

from src.loans.models import Loan


@pytest.mark.django_db
def test_lending_creates_a_formatted_loan_with_escaped_fields(client):
    member = ' Reader; Example\nSecond line '
    isbn = ' 978"xyz '
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
        {'member': 'm' * 256, 'isbn': '123'},
        {'member': 'reader', 'isbn': 'i' * 256},
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
def test_reading_room_lists_loans_and_return_actions(client):
    response = client.get('/ui/loans/')

    assert response.status_code == 200
    assert b'Books in good company.' in response.content
    assert b'href="/ui/loans/new/"' in response.content
    assert b'hx-post="/ui/loans/L1/return/"' in response.content
    assert b'hx-post="/ui/loans/L2/return/"' not in response.content


@pytest.mark.django_db
def test_reading_room_can_lend_and_return_with_htmx(client):
    today = timezone.localdate()
    form_page = client.get('/ui/loans/new/')

    assert form_page.status_code == 200
    assert b'hx-post="/ui/loans/new/"' in form_page.content

    invalid_response = client.post(
        '/ui/loans/new/',
        {'member': ' \t ', 'isbn': ''},
        HTTP_HX_REQUEST='true',
    )

    assert invalid_response.status_code == 200
    assert invalid_response.content.startswith(b'<div id="lend-form-region">')
    assert (
        b'role="alert">Enter a member name; blank values are not accepted.</p>'
        in invalid_response.content
    )
    assert (
        b'role="alert">Enter an ISBN; blank values are not accepted.</p>'
        in invalid_response.content
    )
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
    assert b'Loan L1' in return_response.content
    assert b'role="status">L1 marked returned today.</p>' in return_response.content
    assert b'hx-post="/ui/loans/L1/return/"' not in return_response.content

    repeated_return_response = client.post(
        '/ui/loans/L1/return/',
        HTTP_HX_REQUEST='true',
    )

    assert repeated_return_response.status_code == 200
    assert (
        f'role="status">L1 was already returned on {today.isoformat()}; '
        'repeat return rejected.</p>'.encode()
        in repeated_return_response.content
    )


@pytest.mark.django_db
def test_reading_room_return_redirects_after_first_return(client):
    response = client.post('/ui/loans/L1/return/')

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/'
    assert Loan.objects.get(pk='L1').returned_on == timezone.localdate()


@pytest.mark.django_db
def test_reading_room_returns_useful_responses_for_repeats_and_unknown_loans(client):
    repeated_response = client.post('/ui/loans/L2/return/')

    assert repeated_response.status_code == 409
    assert b'Loan L2 was already returned on Jan 20, 2026.' in repeated_response.content
    assert b'The original return date has been kept.' in repeated_response.content

    missing_response = client.post(
        '/ui/loans/unknown/return/',
        HTTP_HX_REQUEST='true',
    )

    assert missing_response.status_code == 404
    assert missing_response.content.decode() == 'No such loan.'


@pytest.mark.django_db
def test_reading_room_lend_form_handles_regular_posts(client):
    invalid_response = client.post('/ui/loans/new/', {'isbn': '123'})

    assert invalid_response.status_code == 200
    assert b'<!doctype html>' in invalid_response.content
    assert (
        b'role="alert">Enter a member name; blank values are not accepted.</p>'
        in invalid_response.content
    )

    valid_response = client.post(
        '/ui/loans/new/',
        {'member': 'reader', 'isbn': '123'},
    )

    assert valid_response.status_code == 302
    assert valid_response['Location'] == '/ui/loans/'
    assert Loan.objects.get(pk='L4').member == 'reader'


@pytest.mark.django_db
def test_loan_routes_reject_unsupported_methods(client):
    responses = (
        client.put('/loans', {'member': 'reader', 'isbn': '123'}),
        client.get('/loans/L1/return'),
        client.get('/ui/loans/L1/return/'),
        client.put('/ui/loans/new/'),
    )

    assert [response.status_code for response in responses] == [405, 405, 405, 405]
