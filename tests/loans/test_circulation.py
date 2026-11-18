from datetime import date

import pytest
from django.utils import timezone

from src.loans.models import Loan
from src.loans.repository import LoanRepository
from src.loans.services import (
    LoanAlreadyReturned,
    LoanInputError,
    LoanNotFound,
    lend_loan,
    return_loan,
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('member', 'isbn', 'field'),
    [
        (None, '123', 'member'),
        ('', '123', 'member'),
        ('   ', '123', 'member'),
        ('reader', None, 'isbn'),
        ('reader', '', 'isbn'),
        ('reader', '   ', 'isbn'),
    ],
)
def test_lending_use_case_rejects_missing_or_blank_fields(member, isbn, field):
    with pytest.raises(LoanInputError) as error:
        lend_loan(member, isbn, LoanRepository(), date(2026, 3, 1))

    assert field in error.value.errors
    assert Loan.objects.count() == 3


@pytest.mark.django_db
def test_return_use_case_rejects_unknown_loan():
    with pytest.raises(LoanNotFound):
        return_loan('unknown', LoanRepository(), date(2026, 3, 1))


@pytest.mark.django_db
def test_return_use_case_preserves_the_original_date_on_repeat():
    original_date = Loan.objects.get(pk='L2').returned_on

    with pytest.raises(LoanAlreadyReturned):
        return_loan('L2', LoanRepository(), date(2026, 3, 1))

    assert Loan.objects.get(pk='L2').returned_on == original_date


@pytest.mark.django_db
def test_lending_api_returns_the_characterized_record(client):
    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})
    today = timezone.localdate()

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;dee;123;{today.isoformat()};{date.fromordinal(today.toordinal() + 14).isoformat()};\n'
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    'fields',
    [
        {'member': '', 'isbn': '123'},
        {'member': 'reader', 'isbn': '   '},
        {'member': '', 'isbn': ''},
    ],
)
def test_lending_api_rejects_blank_fields(client, fields):
    response = client.post('/loans', fields)

    assert response.status_code == 400
    assert response.content.decode() == 'member and isbn are required\n'


@pytest.mark.django_db
def test_return_api_marks_an_unreturned_loan_and_rejects_a_repeat(client):
    first = client.post('/loans/L1/return')
    returned_on = Loan.objects.get(pk='L1').returned_on
    repeated = client.post('/loans/L1/return')

    assert first.status_code == 200
    assert first.content.decode().startswith('L1;ana;9780134685991;2026-01-02;2026-01-16;')
    assert repeated.status_code == 409
    assert Loan.objects.get(pk='L1').returned_on == returned_on


@pytest.mark.django_db
def test_return_api_preserves_the_characterized_unknown_loan_response(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_lending_page_renders_field_errors_for_blank_values(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': '   ', 'isbn': ''},
    )

    assert response.status_code == 200
    assert b'Member is required.' in response.content
    assert b'ISBN is required.' in response.content
    assert Loan.objects.count() == 3


@pytest.mark.django_db
def test_lending_page_creates_a_loan_and_redirects_to_its_details(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': 'dee', 'isbn': '123'},
    )

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/L4/'


@pytest.mark.django_db
def test_return_page_updates_status_and_rejects_repeated_or_unknown_returns(client):
    returned = client.post('/ui/loans/L1/return/')
    returned_on = Loan.objects.get(pk='L1').returned_on
    repeated = client.post('/ui/loans/L1/return/')
    unknown = client.post('/ui/loans/unknown/return/')

    assert returned.status_code == 302
    assert returned['Location'] == '/ui/loans/L1/'
    assert repeated.status_code == 409
    assert b'already been returned' in repeated.content
    assert Loan.objects.get(pk='L1').returned_on == returned_on
    assert unknown.status_code == 404
    assert b'No such loan' in unknown.content


@pytest.mark.django_db
def test_return_page_supports_htmx_updates(client):
    response = client.post(
        '/ui/loans/L1/return/',
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert b'Returned' in response.content
