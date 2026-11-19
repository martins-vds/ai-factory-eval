from datetime import date

import pytest

from src.loans.models import Loan
from src.loans.repository import LoanRepository
from src.loans.services import LoanAlreadyReturned, LoanInputError, lend_loan, return_loan


@pytest.mark.django_db
def test_lend_endpoint_creates_a_loan_with_the_characterized_record(client, monkeypatch):
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 19))

    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'L4;dee;123;2026-11-19;2026-12-03;\n'
    loan = Loan.objects.get(pk='L4')
    assert loan.member == 'dee'
    assert loan.isbn == '123'
    assert loan.lent_on == date(2026, 11, 19)
    assert loan.due_on == date(2026, 12, 3)


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('member', 'isbn'),
    [('', '123'), ('   ', '123'), ('reader', ''), ('reader', ' \t')],
)
def test_lend_endpoint_rejects_empty_and_whitespace_fields(client, member, isbn):
    response = client.post('/loans', {'member': member, 'isbn': isbn})

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'member and isbn are required\n'


@pytest.mark.django_db
def test_lend_use_case_rejects_blank_fields_without_creating_a_loan():
    repository = LoanRepository()
    before = Loan.objects.count()

    with pytest.raises(LoanInputError) as error:
        lend_loan(repository, '  ', '\t', date(2026, 11, 19))

    assert error.value.fields == {'member': 'Member is required.', 'isbn': 'ISBN is required.'}
    assert Loan.objects.count() == before


@pytest.mark.django_db
def test_return_endpoint_persists_the_return_date(client, monkeypatch):
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 19))

    response = client.post('/loans/L1/return')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;2026-11-19\n'
    assert Loan.objects.get(pk='L1').returned_on == date(2026, 11, 19)


@pytest.mark.django_db
def test_return_use_case_uses_the_supplied_date():
    returned_on = date(2026, 11, 19)

    loan = return_loan(LoanRepository(), 'L1', returned_on)

    assert loan.returned_on == returned_on
    assert Loan.objects.get(pk='L1').returned_on == returned_on


@pytest.mark.django_db
def test_return_use_case_rejects_a_repeat_and_preserves_the_original_date():
    original_date = Loan.objects.get(pk='L2').returned_on

    with pytest.raises(LoanAlreadyReturned):
        return_loan(LoanRepository(), 'L2', date(2026, 11, 19))

    assert Loan.objects.get(pk='L2').returned_on == original_date


@pytest.mark.django_db
def test_return_endpoint_returns_not_found_for_an_unknown_loan(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_return_endpoint_rejects_a_repeat_without_changing_the_date(client):
    original_date = Loan.objects.get(pk='L2').returned_on

    response = client.post('/loans/L2/return')

    assert response.status_code == 409
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'loan has already been returned\n'
    assert Loan.objects.get(pk='L2').returned_on == original_date


@pytest.mark.django_db
def test_reading_room_catalog_links_to_the_lending_form(client):
    response = client.get('/ui/loans/')

    assert response.status_code == 200
    assert b'href="/ui/loans/new/"' in response.content
    assert b'Lend a book' in response.content


@pytest.mark.django_db
def test_full_page_lending_form_shows_field_errors_for_blank_values(client):
    response = client.post('/ui/loans/new/', {'member': ' ', 'isbn': ''})

    assert response.status_code == 200
    assert b'Member is required.' in response.content
    assert b'ISBN is required.' in response.content
    assert Loan.objects.count() == 3


@pytest.mark.django_db
def test_htmx_lending_form_renders_field_errors(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': 'reader', 'isbn': ' \t'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert b'ISBN is required.' in response.content
    assert b'id="lend-form"' in response.content


@pytest.mark.django_db
def test_full_page_lending_redirects_to_the_new_loan(client, monkeypatch):
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 19))

    response = client.post('/ui/loans/new/', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/L4/'


@pytest.mark.django_db
def test_htmx_lending_form_renders_a_successful_loan(client, monkeypatch):
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 19))

    response = client.post(
        '/ui/loans/new/',
        {'member': 'dee', 'isbn': '123'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert b'Loan L4 is ready' in response.content
    assert b'href="/ui/loans/L4/"' in response.content


@pytest.mark.django_db
def test_detail_page_offers_return_for_an_unreturned_loan(client):
    response = client.get('/ui/loans/L1/')

    assert response.status_code == 200
    assert b'hx-post="/ui/loans/L1/return/"' in response.content


@pytest.mark.django_db
def test_htmx_return_page_shows_the_return_date(client, monkeypatch):
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 19))

    response = client.post(
        '/ui/loans/L1/return/',
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert b'Returned Nov 19, 2026' in response.content
    assert Loan.objects.get(pk='L1').returned_on == date(2026, 11, 19)


@pytest.mark.django_db
def test_htmx_repeat_return_renders_error_and_keeps_original_date(client):
    original_date = Loan.objects.get(pk='L2').returned_on

    response = client.post(
        '/ui/loans/L2/return/',
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 409
    assert b'already been returned' in response.content
    assert Loan.objects.get(pk='L2').returned_on == original_date


@pytest.mark.django_db
def test_htmx_unknown_return_renders_not_found(client):
    response = client.post('/ui/loans/unknown/return/', HTTP_HX_REQUEST='true')

    assert response.status_code == 404
    assert b'No such loan.' in response.content
