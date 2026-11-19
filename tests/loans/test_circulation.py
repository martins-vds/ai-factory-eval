from datetime import date, timedelta

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
    ('member', 'isbn', 'invalid_field'),
    [
        (None, '123', 'member'),
        ('', '123', 'member'),
        (' \t', '123', 'member'),
        ('reader', None, 'isbn'),
        ('reader', '', 'isbn'),
        ('reader', ' \t', 'isbn'),
    ],
)
def test_lending_rejects_missing_or_blank_fields(member, isbn, invalid_field):
    loan_count = LoanRepository().all().count()

    with pytest.raises(LoanInputError) as error:
        lend_loan(
            repository=LoanRepository(),
            member=member,
            isbn=isbn,
            lent_on=date(2026, 11, 19),
        )

    assert error.value.fields == {invalid_field: 'This field is required.'}
    assert LoanRepository().all().count() == loan_count


@pytest.mark.django_db
def test_lending_use_case_uses_the_next_id_and_supplied_local_date():
    loan = lend_loan(
        repository=LoanRepository(),
        member=' reader ',
        isbn=' 123 ',
        lent_on=date(2026, 11, 19),
    )

    assert (loan.id, loan.member, loan.isbn, loan.lent_on, loan.due_on) == (
        'L4',
        ' reader ',
        ' 123 ',
        date(2026, 11, 19),
        date(2026, 12, 3),
    )


@pytest.mark.django_db
def test_lending_endpoint_creates_a_loan_and_escapes_delimiters(client):
    today = timezone.localdate()
    response = client.post(
        '/loans',
        {'member': ' Reader; Example ', 'isbn': ' 123;456 '},
    )

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;" Reader; Example ";" 123;456 ";{today.isoformat()};'
        f'{(today + timedelta(days=14)).isoformat()};\n'
    )
    loan = Loan.objects.get(pk='L4')
    assert (loan.member, loan.isbn, loan.lent_on) == (
        ' Reader; Example ',
        ' 123;456 ',
        today,
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    'fields',
    [
        {},
        {'member': 'reader'},
        {'isbn': '123'},
        {'member': '', 'isbn': '123'},
        {'member': 'reader', 'isbn': ''},
    ],
)
def test_lending_endpoint_rejects_empty_fields(client, fields):
    response = client.post('/loans', fields)

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'member and isbn are required\n'
    assert Loan.objects.count() == 3


@pytest.mark.django_db
def test_return_use_case_rejects_repeated_return_without_changing_the_date():
    original_date = Loan.objects.get(pk='L2').returned_on

    with pytest.raises(LoanAlreadyReturned):
        return_loan(
            repository=LoanRepository(),
            loan_id='L2',
            returned_on=date(2026, 11, 19),
        )

    assert Loan.objects.get(pk='L2').returned_on == original_date


@pytest.mark.django_db
def test_return_use_case_stores_the_supplied_date():
    returned_on = date(2026, 11, 19)

    loan = return_loan(
        repository=LoanRepository(),
        loan_id='L1',
        returned_on=returned_on,
    )

    assert loan.returned_on == returned_on
    assert Loan.objects.get(pk='L1').returned_on == returned_on


@pytest.mark.django_db
def test_return_endpoint_records_today_and_returns_the_updated_loan(client):
    today = timezone.localdate()
    response = client.post('/loans/L1/return')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L1;ana;9780134685991;2026-01-02;2026-01-16;{today.isoformat()}\n'
    )
    assert Loan.objects.get(pk='L1').returned_on == today


@pytest.mark.django_db
def test_return_use_case_rejects_an_unknown_loan():
    with pytest.raises(LoanNotFound):
        return_loan(
            repository=LoanRepository(),
            loan_id='unknown',
            returned_on=date(2026, 11, 19),
        )


@pytest.mark.django_db
def test_return_endpoint_rejects_a_repeat_and_keeps_the_original_date(client):
    original_date = Loan.objects.get(pk='L2').returned_on
    response = client.post('/loans/L2/return')

    assert response.status_code == 409
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'loan already returned\n'
    assert Loan.objects.get(pk='L2').returned_on == original_date


@pytest.mark.django_db
def test_return_endpoint_returns_not_found_for_an_unknown_loan(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_new_loan_page_offers_an_htmx_lending_form(client):
    response = client.get('/ui/loans/new/')
    catalog = client.get('/ui/loans/')

    assert response.status_code == 200
    assert catalog.status_code == 200
    assert b'href="/ui/loans/new/"' in catalog.content
    assert b'Loan L1' in catalog.content
    assert b'hx-post="/ui/loans/"' in response.content
    assert b'name="member"' in response.content
    assert b'name="isbn"' in response.content
    assert b'htmx:beforeSwap' in response.content


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('fields', 'error_id', 'retained_value'),
    [
        ({'member': '', 'isbn': '123'}, 'member-error', b'value="123"'),
        ({'member': ' \t', 'isbn': '123'}, 'member-error', b'value="123"'),
        (
            {'member': 'reader', 'isbn': ''},
            'isbn-error',
            b'value="reader"',
        ),
        (
            {'member': 'reader', 'isbn': ' \t'},
            'isbn-error',
            b'value="reader"',
        ),
    ],
)
def test_htmx_lending_form_renders_field_errors(
    client,
    fields,
    error_id,
    retained_value,
):
    response = client.post(
        '/ui/loans/',
        fields,
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 400
    assert b'<!doctype html>' not in response.content
    assert f'id="{error_id}" role="alert"'.encode() in response.content
    assert b'This field is required.' in response.content
    assert retained_value in response.content
    assert b'value="XXXX"' not in response.content


@pytest.mark.django_db
def test_full_page_lending_form_renders_field_errors(client):
    response = client.post(
        '/ui/loans/',
        {'member': '', 'isbn': '123'},
    )

    assert response.status_code == 400
    assert b'<!doctype html>' in response.content
    assert b'id="member-error" role="alert"' in response.content
    assert b'This field is required.' in response.content
    assert b'value="XXXX"' not in response.content
    assert Loan.objects.count() == 3


@pytest.mark.django_db
def test_htmx_lending_form_confirms_the_created_loan(client):
    response = client.post(
        '/ui/loans/',
        {'member': 'reader', 'isbn': '123'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert b'Loan L4 is ready.' in response.content
    assert b'href="/ui/loans/L4/"' in response.content
    assert Loan.objects.get(pk='L4').member == 'reader'


@pytest.mark.django_db
def test_full_page_lending_form_redirects_after_success(client):
    response = client.post(
        '/ui/loans/',
        {'member': 'reader', 'isbn': '123'},
    )

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/'
    assert Loan.objects.get(pk='L4').member == 'reader'


@pytest.mark.django_db
def test_browser_loan_detail_offers_return_and_handles_htmx_errors(client):
    response = client.get('/ui/loans/L1/')

    assert response.status_code == 200
    assert b'hx-post="/ui/loans/L1/return/"' in response.content
    assert b'htmx:beforeSwap' in response.content


@pytest.mark.django_db
def test_htmx_return_marks_the_loan_returned(client):
    response = client.post(
        '/ui/loans/L1/return/',
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert b'role="status"' in response.content
    assert Loan.objects.get(pk='L1').returned_on == timezone.localdate()


@pytest.mark.django_db
def test_htmx_return_renders_unknown_and_repeat_errors(client):
    unknown = client.post(
        '/ui/loans/unknown/return/',
        HTTP_HX_REQUEST='true',
    )
    repeated = client.post(
        '/ui/loans/L2/return/',
        HTTP_HX_REQUEST='true',
    )

    assert unknown.status_code == 404
    assert b'No such loan.' in unknown.content
    assert repeated.status_code == 409
    assert b'This loan was already returned.' in repeated.content
    assert b'Loan record \xc2\xb7 L2' in repeated.content
    assert b'Jan 20, 2026' in repeated.content


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('method', 'path', 'allowed_methods'),
    [
        ('put', '/loans', 'GET, POST'),
        ('put', '/ui/loans/', 'GET, POST'),
        ('post', '/ui/loans/new/', 'GET'),
        ('get', '/loans/L1/return', 'POST'),
        ('get', '/ui/loans/L1/return/', 'POST'),
    ],
)
def test_loan_routes_reject_unsupported_methods(
    client,
    method,
    path,
    allowed_methods,
):
    response = getattr(client, method)(path)

    assert response.status_code == 405
    assert response['Allow'] == allowed_methods
