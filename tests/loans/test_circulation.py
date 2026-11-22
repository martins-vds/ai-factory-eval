from datetime import date, timedelta

import pytest
from django.test import Client

from src.loans.clock import SystemClock
from src.loans.models import Loan
from src.loans.repository import LoanRepository
from src.loans.services import (
    LoanAlreadyReturned,
    LoanInputError,
    LoanNotFound,
    lend_book,
    return_book,
)


@pytest.mark.django_db
def test_lending_api_creates_loan_with_legacy_response(client):
    lent_on = date.today()
    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;dee;123;{lent_on.isoformat()};{(lent_on + timedelta(days=14)).isoformat()};\n'
    )
    loan = Loan.objects.get(pk='L4')
    assert loan.member == 'dee'
    assert loan.isbn == '123'
    assert loan.lent_on == lent_on


@pytest.mark.django_db
def test_legacy_api_posts_do_not_require_browser_csrf_tokens():
    api_client = Client(enforce_csrf_checks=True)

    lend_response = api_client.post('/loans', {'member': 'dee', 'isbn': '123'})
    return_response = api_client.post('/loans/L1/return')
    browser_response = api_client.post('/ui/loans/', {'member': 'dee', 'isbn': '123'})

    assert lend_response.status_code == 201
    assert return_response.status_code == 200
    assert browser_response.status_code == 403


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('member', 'isbn', 'field'),
    [
        (None, '123', 'member'),
        ('', '123', 'member'),
        ('  \t', '123', 'member'),
        ('reader', None, 'isbn'),
        ('reader', '', 'isbn'),
        ('reader', '  \t', 'isbn'),
    ],
)
def test_lending_use_case_rejects_blank_required_fields(member, isbn, field):
    with pytest.raises(LoanInputError) as error:
        lend_book(member, isbn, LoanRepository(), SystemClock())

    assert error.value.field_errors == {field: 'This field is required.'}


@pytest.mark.django_db
@pytest.mark.parametrize(
    'form_data',
    [{'member': 'reader'}, {'isbn': '123'}],
)
def test_lending_api_preserves_missing_field_error_response(client, form_data):
    response = client.post('/loans', form_data)

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'member and isbn are required\n'


@pytest.mark.django_db
@pytest.mark.parametrize(
    'form_data',
    [
        {'member': '', 'isbn': '123'},
        {'member': ' \t', 'isbn': '123'},
        {'member': 'reader', 'isbn': ''},
        {'member': 'reader', 'isbn': ' \t'},
    ],
)
def test_lending_api_rejects_blank_required_fields(client, form_data):
    response = client.post('/loans', form_data)

    assert response.status_code == 400
    assert response.content.decode() == 'member and isbn are required\n'
    assert Loan.objects.count() == 3


@pytest.mark.django_db
def test_return_api_records_first_return_date_and_legacy_response(client):
    returned_on = date.today()

    response = client.post('/loans/L1/return')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L1;ana;9780134685991;2026-01-02;2026-01-16;{returned_on.isoformat()}\n'
    )
    assert Loan.objects.get(pk='L1').returned_on == returned_on


@pytest.mark.django_db
def test_return_api_rejects_repeat_without_replacing_original_date(client):
    original_return_date = date(2026, 1, 20)

    response = client.post('/loans/L2/return')

    assert response.status_code == 409
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'loan already returned\n'
    assert Loan.objects.get(pk='L2').returned_on == original_return_date


@pytest.mark.django_db
def test_return_api_preserves_not_found_response_for_unknown_loan(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_return_use_case_rejects_unknown_loan():
    with pytest.raises(LoanNotFound):
        return_book('unknown', LoanRepository(), SystemClock())


@pytest.mark.django_db
def test_return_use_case_rejects_repeat_without_replacing_original_date():
    original_return_date = date(2026, 1, 20)

    with pytest.raises(LoanAlreadyReturned):
        return_book('L2', LoanRepository(), SystemClock())

    assert Loan.objects.get(pk='L2').returned_on == original_return_date


@pytest.mark.django_db
def test_browser_lending_form_renders_field_errors_for_blank_values(client):
    response = client.post('/ui/loans/', {'member': ' \t', 'isbn': ''})

    assert response.status_code == 400
    assert b'Member' in response.content
    assert b'ISBN' in response.content
    assert response.content.count(b'This field is required.') == 2


@pytest.mark.django_db
def test_browser_lending_form_creates_loan_and_redirects_to_detail(client):
    response = client.post('/ui/loans/', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/L4/'
    loan = Loan.objects.get(pk='L4')
    assert loan.member == 'dee'
    assert loan.isbn == '123'


@pytest.mark.django_db
def test_browser_lending_and_return_actions_use_reading_room_pages(client):
    new_loan_page = client.get('/ui/loans/new/')

    assert new_loan_page.status_code == 200
    assert b'Lend a book.' in new_loan_page.content
    assert b'name="member"' in new_loan_page.content
    assert b'name="isbn"' in new_loan_page.content

    detail_page = client.get('/ui/loans/L1/')

    assert detail_page.status_code == 200
    assert b'hx-post="/ui/loans/L1/return/"' in detail_page.content
    assert b'hx-on::response-error=' in detail_page.content


@pytest.mark.django_db
def test_browser_return_rejection_renders_error_and_original_date(client):
    response = client.post(
        '/ui/loans/L2/return/',
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 409
    assert b'This loan has already been returned.' in response.content
    assert b'Jan 20, 2026' in response.content
    assert Loan.objects.get(pk='L2').returned_on == date(2026, 1, 20)


@pytest.mark.django_db
def test_browser_return_records_date_and_updates_return_status(client):
    returned_on = date.today()

    response = client.post(
        '/ui/loans/L1/return/',
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert (
        f'Returned {returned_on.strftime("%b")} {returned_on.day}, {returned_on.year}'.encode()
        in (response.content)
    )
    assert Loan.objects.get(pk='L1').returned_on == returned_on
