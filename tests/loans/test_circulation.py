from datetime import date, timedelta
from types import SimpleNamespace

import pytest

from src.loans.models import Loan
from src.loans.services import (
    LoanAlreadyReturned,
    LoanInputError,
    LoanNotFound,
    lend_loan,
    loan_line,
    return_loan,
)


@pytest.mark.parametrize(
    ('member', 'isbn', 'field'),
    [('', '123', 'member'), ('reader', '   ', 'isbn')],
)
def test_lend_use_case_rejects_blank_required_fields(member, isbn, field):
    with pytest.raises(LoanInputError) as error:
        lend_loan(object(), member, isbn)

    assert error.value.errors == {field: 'This field is required.'}


def test_return_use_case_rejects_repeat_without_changing_original_date():
    original_date = date(2026, 1, 20)
    loan = SimpleNamespace(returned_on=original_date)

    class Store:
        def find(self, loan_id):
            return loan

        def mark_returned(self, loan_id, returned_on):
            raise AssertionError('a returned loan must not be updated again')

    with pytest.raises(LoanAlreadyReturned):
        return_loan('L1', Store(), date(2026, 11, 21))

    assert loan.returned_on == original_date


def test_return_use_case_reports_unknown_loan():
    class Store:
        def find(self, loan_id):
            return None

        def mark_returned(self, loan_id, returned_on):
            raise AssertionError('an unknown loan must not be updated')

    with pytest.raises(LoanNotFound):
        return_loan('unknown', Store(), date(2026, 11, 21))


def test_return_use_case_records_the_supplied_date():
    loan = SimpleNamespace(returned_on=None)

    class Store:
        def find(self, loan_id):
            return loan

        def mark_returned(self, loan_id, returned_on):
            loan.returned_on = returned_on
            return loan

    returned = return_loan('L1', Store(), date(2026, 11, 21))

    assert returned.returned_on == date(2026, 11, 21)


def test_loan_line_escapes_delimiters_quotes_and_line_breaks():
    loan = SimpleNamespace(
        id='L9',
        member='Reader; Example\nSecond line',
        isbn='978"xyz',
        lent_on=date(2026, 3, 1),
        due_on=date(2026, 3, 15),
        returned_on=None,
    )

    assert loan_line(loan) == (
        'L9;"Reader; Example\nSecond line";"978""xyz";2026-03-01;2026-03-15;\n'
    )


@pytest.mark.django_db
def test_lend_api_creates_a_loan_due_fourteen_days_later(client):
    today = date.today()

    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;dee;123;{today.isoformat()};{(today + timedelta(days=14)).isoformat()};\n'
    )
    loan = Loan.objects.get(pk='L4')
    assert loan.lent_on == today
    assert loan.due_on == today + timedelta(days=14)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'form',
    [
        {'member': '  ', 'isbn': ''},
        {'isbn': '123'},
        {'member': 'reader'},
    ],
)
def test_lend_api_rejects_blank_or_missing_fields_without_creating_a_loan(client, form):
    count_before = Loan.objects.count()

    response = client.post('/loans', form)

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'member and isbn are required\n'
    assert Loan.objects.count() == count_before


@pytest.mark.django_db
def test_return_api_records_first_return_date(client):
    today = date.today()

    response = client.post('/loans/L1/return')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L1;ana;9780134685991;2026-01-02;2026-01-16;{today.isoformat()}\n'
    )
    assert Loan.objects.get(pk='L1').returned_on == today


@pytest.mark.django_db
def test_return_api_rejects_repeat_without_overwriting_original_date(client):
    original_date = date(2026, 1, 20)

    response = client.post('/loans/L2/return')

    assert response.status_code == 409
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'loan already returned\n'
    assert Loan.objects.get(pk='L2').returned_on == original_date


@pytest.mark.django_db
def test_return_api_returns_not_found_for_unknown_loan(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_new_loan_page_displays_reading_room_form(client):
    response = client.get('/ui/loans/new/')

    assert response.status_code == 200
    assert b'<h1' in response.content
    assert b'name="member"' in response.content
    assert b'name="isbn"' in response.content
    assert b'hx-post="/ui/loans/new/"' in response.content


@pytest.mark.django_db
def test_new_loan_page_renders_field_errors_for_blank_values(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': '', 'isbn': '   '},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 422
    assert b'name="member"' in response.content
    assert b'name="isbn"' in response.content
    assert b'member: This field is required.' in response.content
    assert b'isbn: This field is required.' in response.content


@pytest.mark.django_db
def test_successful_lend_from_ui_redirects_to_loan_detail(client):
    response = client.post('/ui/loans/new/', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/L4/'


@pytest.mark.django_db
def test_htmx_lend_redirects_to_loan_detail(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': 'dee', 'isbn': '123'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 201
    assert response['HX-Redirect'] == '/ui/loans/L4/'


@pytest.mark.django_db
def test_return_ui_shows_success_and_rejects_a_second_return(client):
    first = client.post('/ui/loans/L1/return/', HTTP_HX_REQUEST='true')

    assert first.status_code == 200
    assert b'Returned' in first.content
    original_date = Loan.objects.get(pk='L1').returned_on
    assert original_date == date.today()

    repeated = client.post('/ui/loans/L1/return/', HTTP_HX_REQUEST='true')

    assert repeated.status_code == 409
    assert b'already returned' in repeated.content
    assert Loan.objects.get(pk='L1').returned_on == original_date


@pytest.mark.django_db
def test_return_ui_renders_unknown_loan_error(client):
    response = client.post('/ui/loans/unknown/return/', HTTP_HX_REQUEST='true')

    assert response.status_code == 404
    assert b'no such loan' in response.content
