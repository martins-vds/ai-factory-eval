from datetime import date, timedelta
from types import SimpleNamespace

import pytest
from django.utils import timezone

from src.loans.services import (
    LoanAlreadyReturnedError,
    LoanNotFoundError,
    LoanValidationError,
    lend_loan,
    return_loan,
)


class LoanStore:
    def __init__(self, loans=()):
        self.created = []
        self.loans = {loan.id: loan for loan in loans}

    def next_id(self):
        return f'L{len(self.created) + 1}'

    def create(self, **fields):
        self.created.append(fields)
        return fields

    def find(self, loan_id):
        return self.loans.get(loan_id)

    def return_if_unreturned(self, loan_id, returned_on):
        loan = self.find(loan_id)
        if loan is None or loan.returned_on is not None:
            return False
        loan.returned_on = returned_on
        return True


@pytest.mark.parametrize(
    ('member', 'isbn', 'field'),
    [
        (' \t', '123', 'member'),
        ('reader', '\n ', 'isbn'),
    ],
)
def test_lend_use_case_rejects_blank_fields_without_creating_a_loan(member, isbn, field):
    store = LoanStore()

    with pytest.raises(LoanValidationError) as error:
        lend_loan(member, isbn, date(2026, 11, 18), store)

    assert error.value.errors == {field: 'This field is required.'}
    assert store.created == []


@pytest.mark.django_db
def test_lend_api_creates_a_loan_with_the_characterized_response(client):
    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})
    lent_on = timezone.localdate()

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;dee;123;{lent_on.isoformat()};{(lent_on + timedelta(days=14)).isoformat()};\n'
    )


@pytest.mark.django_db
def test_lend_api_escapes_semicolons_in_created_loan_fields(client):
    lent_on = timezone.localdate()
    response = client.post('/loans', {'member': 'reader;one', 'isbn': '123;456'})

    assert response.status_code == 201
    assert response.content.decode() == (
        f'L4;"reader;one";"123;456";{lent_on.isoformat()};'
        f'{(lent_on + timedelta(days=14)).isoformat()};\n'
    )


@pytest.mark.parametrize(
    'form',
    [
        {'isbn': '123'},
        {'member': 'reader'},
        {'member': '', 'isbn': '123'},
        {'member': ' \t ', 'isbn': '123'},
        {'member': 'reader', 'isbn': ''},
        {'member': 'reader', 'isbn': '\n'},
    ],
)
@pytest.mark.django_db
def test_lend_api_rejects_missing_or_blank_required_fields(client, form):
    response = client.post('/loans', form)

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'member and isbn are required\n'


def test_return_use_case_rejects_a_repeat_and_preserves_the_original_date():
    original_date = date(2026, 11, 17)
    loan = SimpleNamespace(id='L1', returned_on=original_date)
    store = LoanStore([loan])

    with pytest.raises(LoanAlreadyReturnedError):
        return_loan('L1', date(2026, 11, 18), store)

    assert loan.returned_on == original_date


def test_return_use_case_records_the_requested_date():
    loan = SimpleNamespace(id='L1', returned_on=None)
    store = LoanStore([loan])

    returned_loan = return_loan('L1', date(2026, 11, 18), store)

    assert returned_loan.returned_on == date(2026, 11, 18)


def test_return_use_case_rejects_an_unknown_loan():
    with pytest.raises(LoanNotFoundError):
        return_loan('missing', date(2026, 11, 18), LoanStore())


@pytest.mark.django_db
def test_return_api_records_date_and_rejects_repeated_returns(client):
    returned_on = timezone.localdate()

    first_return = client.post('/loans/L1/return')
    repeated_return = client.post('/loans/L1/return')
    loan_record = client.get('/loans/L1')

    assert first_return.status_code == 200
    assert first_return['Content-Type'] == 'text/plain'
    assert first_return.content.decode() == (
        f'L1;ana;9780134685991;2026-01-02;2026-01-16;{returned_on.isoformat()}\n'
    )
    assert repeated_return.status_code == 409
    assert repeated_return['Content-Type'] == 'text/plain'
    assert repeated_return.content.decode() == 'loan already returned\n'
    assert loan_record.content.decode().endswith(f'{returned_on.isoformat()}\n')


@pytest.mark.django_db
def test_return_api_returns_not_found_for_unknown_loan(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_loan_list_renders_reading_room_lend_form_using_a_ui_route(client):
    response = client.get('/ui/loans/')

    assert response.status_code == 200
    assert b'Books in good company.' in response.content
    assert b'hx-post="/ui/loans/new/"' in response.content
    assert b'name="member"' in response.content
    assert b'name="isbn"' in response.content
    assert b'Loan L1' in response.content


@pytest.mark.django_db
def test_full_page_lending_creates_and_displays_the_new_loan(client):
    response = client.post('/ui/loans/new/', {'member': 'reader', 'isbn': '123'})

    assert response.status_code == 201
    assert b'Books in good company.' in response.content
    assert b'Loan L4 has been added.' in response.content
    assert b'Loan L4' in response.content


@pytest.mark.django_db
def test_ui_lending_creates_a_loan_and_refreshes_the_record_list(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': 'reader', 'isbn': '123'},
        HTTP_HX_REQUEST='true',
    )
    records = client.get('/ui/loans/records/')

    assert response.status_code == 201
    assert response['HX-Trigger'] == 'loan-updated'
    assert b'Loan L4 has been added.' in response.content
    assert b'Loan L4' in records.content


@pytest.mark.parametrize(
    'headers',
    [{}, {'HTTP_HX_REQUEST': 'true'}],
)
@pytest.mark.django_db
def test_ui_lending_renders_field_errors_for_full_page_and_htmx_requests(client, headers):
    response = client.post('/ui/loans/new/', {'member': ' \t ', 'isbn': '123'}, **headers)

    assert response.status_code == 400
    assert b'Member:' in response.content
    assert b'This field is required.' in response.content
    if headers:
        assert b'The Lending Library' not in response.content
    else:
        assert b'The Lending Library' in response.content
        assert b'Loan L1' in response.content
        assert b'value=" \t "' in response.content
        assert b'value="123"' in response.content


@pytest.mark.parametrize(
    ('form', 'expected_member', 'expected_isbn'),
    [
        ({'isbn': '123'}, b'value=""', b'value="123"'),
        ({'member': 'reader'}, b'value="reader"', b'value=""'),
    ],
)
@pytest.mark.django_db
def test_full_page_lending_keeps_empty_defaults_for_missing_fields(
    client, form, expected_member, expected_isbn
):
    response = client.post('/ui/loans/new/', form)

    assert response.status_code == 400
    assert expected_member in response.content
    assert expected_isbn in response.content


@pytest.mark.django_db
def test_open_loan_detail_offers_a_return_action_on_the_ui_route(client):
    response = client.get('/ui/loans/L1/')

    assert response.status_code == 200
    assert b'hx-post="/ui/loans/L1/return/"' in response.content
    assert b'hx-on::before-swap=' in response.content


@pytest.mark.django_db
def test_ui_return_rejects_repeated_returns_and_preserves_the_original_date(client):
    first = client.post('/ui/loans/L1/return/', HTTP_HX_REQUEST='true')
    repeated = client.post('/ui/loans/L1/return/', HTTP_HX_REQUEST='true')
    current_record = client.get('/loans/L1')

    assert first.status_code == 200
    assert first['HX-Trigger'] == 'loan-updated'
    assert b'Returned on' in first.content
    assert repeated.status_code == 409
    assert b'already been returned' in repeated.content
    assert b'Returned on' in repeated.content
    assert current_record.content.decode().endswith(f'{timezone.localdate().isoformat()}\n')


@pytest.mark.django_db
def test_ui_return_renders_a_not_found_response_for_unknown_loans(client):
    response = client.post('/ui/loans/unknown/return/')

    assert response.status_code == 404
    assert b'No such loan.' in response.content


@pytest.mark.django_db
def test_ui_return_renders_unknown_loan_error_as_an_htmx_fragment(client):
    response = client.post('/ui/loans/unknown/return/', HTTP_HX_REQUEST='true')

    assert response.status_code == 404
    assert b'No such loan.' in response.content
    assert b'The Lending Library' not in response.content


@pytest.mark.django_db
def test_full_page_return_redirects_then_displays_repeated_return_details(client):
    first = client.post('/ui/loans/L1/return/')
    repeated = client.post('/ui/loans/L1/return/')

    assert first.status_code == 302
    assert first['Location'] == '/ui/loans/L1/'
    assert repeated.status_code == 409
    assert b'Loan record \xc2\xb7 L1' in repeated.content
    assert b'This loan has already been returned.' in repeated.content
    assert b'Returned on' in repeated.content


@pytest.mark.django_db
def test_loan_mutation_endpoints_reject_unsupported_methods(client):
    assert client.put('/loans').status_code == 405
    assert client.get('/loans/L1/return').status_code == 405
    assert client.get('/ui/loans/new/').status_code == 405
    assert client.get('/ui/loans/L1/return/').status_code == 405
