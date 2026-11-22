from datetime import date

import pytest

from src.loans.models import Loan
from src.loans.repository import LoanRepository
from src.loans.services import (
    LoanAlreadyReturned,
    LoanNotFound,
    LoanValidationError,
    lend_book,
    return_book,
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('member', 'isbn', 'field'),
    [
        ('', '123', 'member'),
        ('reader', '', 'isbn'),
        ('   ', '123', 'member'),
        ('reader', '   ', 'isbn'),
    ],
)
def test_lend_use_case_rejects_blank_fields(member, isbn, field):
    before = Loan.objects.count()

    with pytest.raises(LoanValidationError) as error:
        lend_book(LoanRepository(), date(2026, 11, 22), member, isbn)

    assert error.value.errors == {field: 'This field is required.'}
    assert Loan.objects.count() == before


@pytest.mark.django_db
def test_lend_use_case_assigns_the_next_id_and_lending_date():
    loan = lend_book(LoanRepository(), date(2026, 11, 22), 'reader', '123')

    assert (loan.id, loan.member, loan.isbn, loan.lent_on, loan.due_on) == (
        'L4',
        'reader',
        '123',
        date(2026, 11, 22),
        date(2026, 12, 6),
    )


@pytest.mark.django_db
def test_return_use_case_sets_date_once_and_rejects_a_repeat():
    repository = LoanRepository()
    returned = return_book(repository, 'L1', date(2026, 11, 22))

    assert returned.returned_on == date(2026, 11, 22)
    assert Loan.objects.get(pk='L1').returned_on == date(2026, 11, 22)
    with pytest.raises(LoanAlreadyReturned):
        return_book(repository, 'L1', date(2026, 11, 23))
    assert Loan.objects.get(pk='L1').returned_on == date(2026, 11, 22)


@pytest.mark.django_db
def test_return_use_case_rejects_unknown_loan_without_creating_it():
    before = Loan.objects.count()

    with pytest.raises(LoanNotFound):
        return_book(LoanRepository(), 'unknown', date(2026, 11, 22))

    assert Loan.objects.count() == before


@pytest.mark.django_db
def test_lend_endpoint_creates_a_dated_loan(client, monkeypatch):
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 22))

    response = client.post('/loans', {'member': 'reader', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'L4;reader;123;2026-11-22;2026-12-06;\n'
    loan = Loan.objects.get(pk='L4')
    assert (loan.member, loan.isbn, loan.lent_on, loan.returned_on) == (
        'reader',
        '123',
        date(2026, 11, 22),
        None,
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    'form',
    [
        {'member': '', 'isbn': '123'},
        {'member': 'reader', 'isbn': '   '},
        {'member': 'reader'},
        {'isbn': '123'},
    ],
)
def test_lend_endpoint_rejects_missing_or_blank_fields(client, form):
    before = Loan.objects.count()

    response = client.post('/loans', form)

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'member and isbn are required\n'
    assert Loan.objects.count() == before


@pytest.mark.django_db
def test_lend_endpoint_escapes_delimiters_in_export(client, monkeypatch):
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 22))

    response = client.post('/loans', {'member': 'Reader; One', 'isbn': '123;456'})

    assert response.status_code == 201
    assert response.content.decode() == ('L4;"Reader; One";"123;456";2026-11-22;2026-12-06;\n')


@pytest.mark.django_db
def test_return_endpoint_sets_date_once_and_rejects_a_repeat(client, monkeypatch):
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 22))

    first_response = client.post('/loans/L1/return')

    assert first_response.status_code == 200
    assert first_response.content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;2026-11-22\n'
    )
    assert Loan.objects.get(pk='L1').returned_on == date(2026, 11, 22)

    second_response = client.post('/loans/L1/return')

    assert second_response.status_code == 409
    assert second_response.content.decode() == 'loan is already returned\n'
    assert Loan.objects.get(pk='L1').returned_on == date(2026, 11, 22)


@pytest.mark.django_db
def test_return_endpoint_returns_not_found_for_unknown_loan(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_ui_lending_page_renders_field_errors_for_full_and_htmx_requests(client):
    page = client.get('/ui/loans/new/')

    assert page.status_code == 200
    assert b'Loan a book' in page.content
    assert b'name="member"' in page.content
    assert b'name="isbn"' in page.content

    form_data = {'member': 'reader', 'isbn': '   '}
    full_page_error = client.post('/ui/loans/new/', form_data)
    htmx_error = client.post('/ui/loans/new/', form_data, HTTP_HX_REQUEST='true')

    for response in (full_page_error, htmx_error):
        assert response.status_code == 400
        assert b'This field is required.' in response.content
        assert b'value="reader"' in response.content

    assert b'hx-on::before-swap' in htmx_error.content


@pytest.mark.django_db
def test_ui_lend_redirects_to_the_new_loan_detail(client, monkeypatch):
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 22))

    response = client.post(
        '/ui/loans/new/',
        {'member': 'reader', 'isbn': '123'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 204
    assert response['HX-Redirect'] == '/ui/loans/L4/'
    assert Loan.objects.get(pk='L4').lent_on == date(2026, 11, 22)


@pytest.mark.django_db
def test_ui_return_rejects_repeated_returns_without_replacing_date(client, monkeypatch):
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 22))
    detail = client.get('/ui/loans/L1/')

    assert detail.status_code == 200
    assert b'hx-on::before-swap' in detail.content

    first_response = client.post(
        '/ui/loans/L1/return/',
        HTTP_HX_REQUEST='true',
    )

    assert first_response.status_code == 204
    assert first_response['HX-Redirect'] == '/ui/loans/L1/'
    assert Loan.objects.get(pk='L1').returned_on == date(2026, 11, 22)

    second_response = client.post(
        '/ui/loans/L1/return/',
        HTTP_HX_REQUEST='true',
    )

    assert second_response.status_code == 409
    assert b'already been returned' in second_response.content.lower()
    assert b'already been returned' in second_response.content.lower()
    assert Loan.objects.get(pk='L1').returned_on == date(2026, 11, 22)


@pytest.mark.django_db
def test_ui_return_for_unknown_loan_renders_error(client):
    response = client.post(
        '/ui/loans/unknown/return/',
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 404
    assert b'No such loan.' in response.content
