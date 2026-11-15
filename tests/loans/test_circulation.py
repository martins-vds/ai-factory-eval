from datetime import date

import pytest
from django.test import Client
from django.utils import timezone

from src.loans.models import Loan


@pytest.mark.django_db
def test_lending_creates_a_loan_with_a_fourteen_day_due_date(client, monkeypatch):
    today = date(2026, 11, 15)
    monkeypatch.setattr(timezone, 'localdate', lambda: today)
    due_on = date.fromordinal(today.toordinal() + 14)

    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == f'L4;dee;123;{today};{due_on};\n'
    loan = Loan.objects.get(pk='L4')
    assert loan.lent_on == today
    assert loan.due_on == due_on


@pytest.mark.django_db
def test_api_lending_matches_characterization_golden(client, monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 11, 8))

    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'L4;dee;123;2026-11-08;2026-11-22;\n'


@pytest.mark.django_db
def test_first_return_matches_characterization_golden(client, monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 11, 8))

    response = client.post('/loans/L1/return')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == ('L1;ana;9780134685991;2026-01-02;2026-01-16;2026-11-08\n')


@pytest.mark.parametrize(
    'form_data',
    [
        {},
        {'member': '', 'isbn': '123'},
        {'member': 'dee', 'isbn': ''},
        {'member': '  ', 'isbn': '123'},
        {'member': 'dee', 'isbn': '  '},
    ],
)
@pytest.mark.django_db
def test_lending_rejects_missing_or_blank_fields(client, form_data):
    response = client.post('/loans', form_data)

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'member and isbn are required\n'
    assert Loan.objects.count() == 3


@pytest.mark.django_db
def test_lending_quotes_delimiter_characters(client, monkeypatch):
    today = date(2026, 11, 15)
    monkeypatch.setattr(timezone, 'localdate', lambda: today)

    response = client.post(
        '/loans',
        {'member': 'a;b', 'isbn': '123;456'},
    )

    assert response.status_code == 201
    assert response.content.decode() == 'L4;"a;b";"123;456";2026-11-15;2026-11-29;\n'


@pytest.mark.django_db
def test_returning_a_loan_persists_today_and_returns_its_record(client, monkeypatch):
    today = date(2026, 11, 15)
    monkeypatch.setattr(timezone, 'localdate', lambda: today)

    response = client.post('/loans/L1/return')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == ('L1;ana;9780134685991;2026-01-02;2026-01-16;2026-11-15\n')
    assert Loan.objects.get(pk='L1').returned_on == today


@pytest.mark.django_db
def test_returning_an_unknown_loan_returns_not_found(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_repeated_return_is_rejected_without_changing_the_date(client, monkeypatch):
    original_date = date(2026, 1, 20)
    Loan.objects.filter(pk='L2').update(returned_on=original_date)
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 11, 15))

    response = client.post('/loans/L2/return')

    assert response.status_code == 409
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'loan already returned\n'
    assert Loan.objects.get(pk='L2').returned_on == original_date


@pytest.mark.django_db
def test_htmx_can_lend_and_return_a_book_with_csrf(monkeypatch):
    today = date(2026, 11, 15)
    monkeypatch.setattr(timezone, 'localdate', lambda: today)
    csrf_client = Client(enforce_csrf_checks=True)
    page = csrf_client.get('/ui/loans/')
    assert b'name="csrfmiddlewaretoken"' in page.content
    csrf_token = csrf_client.cookies['csrftoken'].value

    lend_response = csrf_client.post(
        '/ui/loans/new/',
        {
            'member': 'reader',
            'isbn': '9780000000001',
            'csrfmiddlewaretoken': csrf_token,
        },
        HTTP_HX_REQUEST='true',
    )
    assert lend_response.status_code == 200
    assert b'id="loan-L4"' in lend_response.content
    assert b'reader \xc2\xb7 ISBN 9780000000001' in lend_response.content
    assert b'On loan' in lend_response.content

    return_response = csrf_client.post(
        '/ui/loans/L4/return/',
        {'csrfmiddlewaretoken': csrf_token},
        HTTP_HX_REQUEST='true',
    )
    assert return_response.status_code == 200
    assert b'Returned Nov 15, 2026' in return_response.content
    assert Loan.objects.get(pk='L4').returned_on == today


@pytest.mark.django_db
def test_reading_room_shows_field_errors_for_blank_loan_details(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': '  ', 'isbn': ''},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert b'Member is required.' in response.content
    assert b'ISBN is required.' in response.content
    assert Loan.objects.count() == 3
