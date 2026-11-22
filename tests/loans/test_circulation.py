from datetime import date, timedelta

import pytest
from django.utils import timezone

from src.loans.models import Loan
from src.loans.repository import LoanRepository
from src.loans.services import AlreadyReturned, InvalidLoanInput, lend_loan, return_loan


class UnusedRepository:
    def __getattr__(self, name):
        pytest.fail(f"invalid lending input must be rejected before repository access: {name}")


@pytest.mark.parametrize(
    ('member', 'isbn', 'field'),
    [
        (None, '123', 'member'),
        (' \t', '123', 'member'),
        ('reader', None, 'isbn'),
        ('reader', '\n ', 'isbn'),
    ],
)
def test_lending_use_case_rejects_missing_and_blank_fields(member, isbn, field):
    with pytest.raises(InvalidLoanInput) as error:
        lend_loan(member, isbn, UnusedRepository(), date(2026, 3, 1))

    assert set(error.value.errors) == {field}


@pytest.mark.django_db
def test_lending_use_case_creates_a_fourteen_day_loan():
    loan = lend_loan('reader', '123', LoanRepository(), date(2026, 3, 1))

    assert loan.id == 'L4'
    assert loan.lent_on == date(2026, 3, 1)
    assert loan.due_on == date(2026, 3, 15)
    assert Loan.objects.get(pk='L4') == loan


@pytest.mark.django_db
def test_return_use_case_returns_none_for_an_unknown_loan():
    assert return_loan('unknown', LoanRepository(), date(2026, 3, 1)) is None


@pytest.mark.django_db
def test_return_use_case_records_the_supplied_date():
    loan = return_loan('L1', LoanRepository(), date(2026, 3, 1))

    assert loan.returned_on == date(2026, 3, 1)
    assert Loan.objects.get(pk='L1').returned_on == date(2026, 3, 1)


@pytest.mark.django_db
def test_return_use_case_rejects_a_repeat_and_preserves_the_original_date():
    original_return_date = Loan.objects.get(pk='L2').returned_on

    with pytest.raises(AlreadyReturned):
        return_loan('L2', LoanRepository(), date(2026, 3, 1))

    assert Loan.objects.get(pk='L2').returned_on == original_return_date


@pytest.mark.django_db
def test_lending_api_preserves_the_characterized_response(client):
    response = client.post('/loans', {'member': 'reader', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;reader;123;{timezone.localdate().isoformat()};'
        f'{(timezone.localdate() + timedelta(days=14)).isoformat()};\n'
    )


@pytest.mark.django_db
def test_lending_api_rejects_blank_fields_with_legacy_error(client):
    response = client.post('/loans', {'member': '  ', 'isbn': '123'})

    assert response.status_code == 400
    assert response.content.decode() == 'member and isbn are required\n'


@pytest.mark.django_db
def test_lending_api_preserves_missing_field_error(client):
    response = client.post('/loans', {'member': 'reader'})

    assert response.status_code == 400
    assert response.content.decode() == 'member and isbn are required\n'


@pytest.mark.django_db
def test_lending_api_escapes_delimiters_and_line_breaks(client):
    response = client.post('/loans', {'member': 'Reader; Example\nSecond line', 'isbn': '978"xyz'})

    assert response.status_code == 201
    assert response.content.decode().startswith('L4;"Reader; Example\nSecond line";"978""xyz";')


@pytest.mark.django_db
def test_return_api_keeps_the_first_return_date(client):
    original_return_date = Loan.objects.get(pk='L2').returned_on

    response = client.post('/loans/L2/return')

    assert response.status_code == 409
    assert response.content.decode() == 'loan already returned\n'
    assert Loan.objects.get(pk='L2').returned_on == original_return_date


@pytest.mark.django_db
def test_return_api_preserves_the_characterized_response(client):
    response = client.post('/loans/L1/return')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode().endswith(f'{timezone.localdate().isoformat()}\n')


@pytest.mark.django_db
def test_return_api_returns_not_found_for_an_unknown_loan(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_reading_room_catalog_offers_lending_and_return_actions(client):
    response = client.get('/ui/loans/')

    assert response.status_code == 200
    assert b'href="/ui/loans/new/"' in response.content
    assert b'hx-post="/ui/loans/L1/return/"' in response.content
    assert b'hx-on::before-swap=' in response.content


@pytest.mark.django_db
def test_reading_room_lend_form_renders_field_errors_for_htmx(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': '  ', 'isbn': '123'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 422
    assert b'id="member-error"' in response.content
    assert b'This field is required.' in response.content
    assert b'hx-swap' in response.content


@pytest.mark.django_db
def test_reading_room_lend_form_creates_a_loan_for_htmx(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': 'reader', 'isbn': '123'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 201
    assert b'Loan L4 is ready.' in response.content
    assert Loan.objects.get(pk='L4').member == 'reader'


@pytest.mark.django_db
def test_reading_room_return_renders_repeat_return_error_for_htmx(client):
    response = client.post('/ui/loans/L2/return/', HTTP_HX_REQUEST='true')

    assert response.status_code == 409
    assert b'already been returned' in response.content
