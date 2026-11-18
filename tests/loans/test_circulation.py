from datetime import date, timedelta
from types import SimpleNamespace

import pytest
from django.test import Client
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
    assert error.value.errors[field] == (
        'Member is required.' if field == 'member' else 'ISBN is required.'
    )
    assert Loan.objects.count() == 3


@pytest.mark.django_db
def test_lending_use_case_creates_a_loan_for_the_supplied_date():
    loan = lend_loan('dee', '123', LoanRepository(), date(2026, 3, 1))

    assert loan.id == 'L4'
    assert loan.lent_on == date(2026, 3, 1)
    assert loan.due_on == date(2026, 3, 15)


@pytest.mark.django_db
def test_lending_repository_assigns_the_next_loan_id():
    loan = LoanRepository().create(
        member='dee',
        isbn='123',
        lent_on=date(2026, 3, 1),
    )

    assert loan.id == 'L4'


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
def test_return_use_case_records_the_supplied_date():
    loan = return_loan('L1', LoanRepository(), date(2026, 3, 1))

    assert loan.returned_on == date(2026, 3, 1)
    assert Loan.objects.get(pk='L1').returned_on == date(2026, 3, 1)


@pytest.mark.parametrize(
    ('second_lookup', 'expected_error'),
    [
        (None, LoanNotFound),
        (SimpleNamespace(returned_on=date(2026, 3, 1)), LoanAlreadyReturned),
    ],
)
def test_return_use_case_classifies_a_failed_conditional_update(
    second_lookup,
    expected_error,
):
    class RacingRepository:
        def __init__(self):
            self.lookup_results = [SimpleNamespace(returned_on=None), second_lookup]

        def find(self, loan_id):
            return self.lookup_results.pop(0)

        def record_return(self, loan_id, today):
            return None

    repository = RacingRepository()

    with pytest.raises(expected_error):
        return_loan('L1', repository, date(2026, 3, 2))

    assert repository.lookup_results == []


@pytest.mark.django_db
def test_repository_cannot_replace_a_return_date():
    repository = LoanRepository()

    first = repository.record_return('L1', date(2026, 3, 1))
    repeated = repository.record_return('L1', date(2026, 3, 2))

    assert first.returned_on == date(2026, 3, 1)
    assert repeated is None
    assert Loan.objects.get(pk='L1').returned_on == date(2026, 3, 1)


@pytest.mark.django_db
def test_lending_api_returns_the_characterized_record(client):
    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})
    today = timezone.localdate()

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;dee;123;{today.isoformat()};{(today + timedelta(days=14)).isoformat()};\n'
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    'fields',
    [
        {'isbn': '123'},
        {'member': 'reader'},
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
    assert first.content.decode() == (
        f'L1;ana;9780134685991;2026-01-02;2026-01-16;{timezone.localdate().isoformat()}\n'
    )
    assert repeated.status_code == 409
    assert repeated.content.decode() == 'loan already returned\n'
    assert Loan.objects.get(pk='L1').returned_on == returned_on


@pytest.mark.django_db
def test_return_api_preserves_the_characterized_unknown_loan_response(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_api_write_endpoints_do_not_require_browser_csrf_tokens():
    client = Client(enforce_csrf_checks=True)

    lending = client.post('/loans', {'member': 'dee', 'isbn': '123'})
    returning = client.post('/loans/L1/return')

    assert lending.status_code == 201
    assert returning.status_code == 200


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
@pytest.mark.parametrize(
    ('fields', 'error'),
    [
        ({'isbn': '123'}, b'Member is required.'),
        ({'member': 'reader'}, b'ISBN is required.'),
        ({'member': '', 'isbn': '123'}, b'Member is required.'),
    ],
)
def test_lending_page_renders_required_field_errors(client, fields, error):
    response = client.post('/ui/loans/new/', fields)

    assert response.status_code == 200
    assert error in response.content


@pytest.mark.django_db
def test_htmx_lending_page_renders_blank_field_errors(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': '   ', 'isbn': '   '},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert b'Member is required.' in response.content
    assert b'ISBN is required.' in response.content


@pytest.mark.django_db
def test_lending_page_creates_a_loan_and_redirects_to_its_details(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': 'dee', 'isbn': '123'},
    )

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/L4/'


@pytest.mark.django_db
def test_lending_page_preserves_nonblank_whitespace(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': ' dee ', 'isbn': ' 123 '},
    )
    assert response.status_code == 302
    detail = client.get(response['Location'])

    assert b' dee  \xc2\xb7 ISBN  123 ' in detail.content


@pytest.mark.django_db
def test_lending_page_is_linked_from_the_reading_room_list(client):
    response = client.get('/ui/loans/')

    assert response.status_code == 200
    assert b'href="/ui/loans/new/"' in response.content

    lending_page = client.get('/ui/loans/new/')

    assert lending_page.status_code == 200
    assert b'hx-post="/ui/loans/new/"' in lending_page.content


@pytest.mark.django_db
def test_unknown_loan_detail_renders_the_reading_room_not_found_page(client):
    response = client.get('/ui/loans/unknown/')

    assert response.status_code == 404
    assert b'No such loan.' in response.content


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
def test_htmx_return_errors_render_without_changing_the_return_date(client):
    repeated = client.post(
        '/ui/loans/L2/return/',
        HTTP_HX_REQUEST='true',
    )
    unknown = client.post(
        '/ui/loans/unknown/return/',
        HTTP_HX_REQUEST='true',
    )

    assert repeated.status_code == 200
    assert b'already been returned' in repeated.content
    assert Loan.objects.get(pk='L2').returned_on == date(2026, 1, 20)
    assert unknown.status_code == 200
    assert b'No such loan' in unknown.content


@pytest.mark.django_db
def test_return_page_supports_htmx_updates(client):
    response = client.post(
        '/ui/loans/L1/return/',
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert b'Returned' in response.content
