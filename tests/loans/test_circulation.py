from datetime import date

import pytest
from django.utils import timezone

from src.loans.models import Loan


@pytest.mark.django_db
def test_lend_endpoint_creates_a_loan_with_a_fourteen_day_due_date(client, monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 3, 1))

    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'L4;dee;123;2026-03-01;2026-03-15;\n'
    loan = Loan.objects.get(pk='L4')
    assert loan.lent_on == date(2026, 3, 1)
    assert loan.due_on == date(2026, 3, 15)


@pytest.mark.parametrize(
    'fields',
    [
        {'member': 'reader'},
        {'isbn': '123'},
        {'member': '', 'isbn': '123'},
        {'member': ' \t ', 'isbn': '123'},
        {'member': 'reader', 'isbn': ''},
        {'member': 'reader', 'isbn': '\n '},
    ],
)
@pytest.mark.django_db
def test_lend_endpoint_rejects_missing_or_blank_fields(client, fields):
    response = client.post('/loans', fields)

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'member and isbn are required\n'
    assert Loan.objects.count() == 3


@pytest.mark.django_db
def test_return_endpoint_persists_today_and_rejects_a_second_return(
    client, monkeypatch
):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 3, 1))

    first_response = client.post('/loans/L1/return')

    assert first_response.status_code == 200
    assert first_response['Content-Type'] == 'text/plain'
    assert first_response.content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;2026-03-01\n'
    )
    assert Loan.objects.get(pk='L1').returned_on == date(2026, 3, 1)

    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 3, 2))
    repeated_response = client.post('/loans/L1/return')

    assert repeated_response.status_code == 409
    assert repeated_response.content.decode() == 'loan already returned\n'
    assert Loan.objects.get(pk='L1').returned_on == date(2026, 3, 1)


@pytest.mark.django_db
def test_return_endpoint_preserves_not_found_response(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_lending_page_renders_field_errors_for_blank_values(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': '  ', 'isbn': '123'},
    )

    assert response.status_code == 200
    assert b'Member is required.' in response.content
    assert b'ISBN is required.' not in response.content
    assert Loan.objects.count() == 3


@pytest.mark.django_db
def test_browser_can_lend_and_return_using_ui_routes(client, monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 3, 1))

    lend_page = client.get('/ui/loans/new/')

    assert lend_page.status_code == 200
    assert b'Borrower' in lend_page.content
    assert b'ISBN' in lend_page.content

    lend_response = client.post(
        '/ui/loans/new/',
        {'member': 'dee', 'isbn': '123'},
    )

    assert lend_response.status_code == 302
    assert lend_response['Location'] == '/ui/loans/L4/'

    return_response = client.post(
        '/ui/loans/L4/return/',
        HTTP_HX_REQUEST='true',
    )

    assert return_response.status_code == 200
    assert b'Returned Mar 1, 2026' in return_response.content
    assert b'Mark returned' not in return_response.content
    assert Loan.objects.get(pk='L4').returned_on == date(2026, 3, 1)
