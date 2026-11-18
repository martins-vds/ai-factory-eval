from datetime import date

import pytest

from src.loans.models import Loan
from src.loans.repository import LoanRepository
from src.loans.services import (
    LoanAlreadyReturned,
    LoanInputError,
    LoanNotFound,
    lend_loan,
    return_loan,
)


class FixedClock:
    def __init__(self, current_date=date(2026, 11, 18)):
        self.current_date = current_date

    def today(self):
        return self.current_date


@pytest.mark.parametrize(
    ('field', 'value'),
    [
        ('member', None),
        ('member', ''),
        ('member', ' \t'),
        ('isbn', None),
        ('isbn', ''),
        ('isbn', ' \t'),
    ],
)
def test_lend_use_case_rejects_blank_member_and_isbn(field, value):
    class Repository:
        def create(self, **fields):
            pytest.fail('invalid lending input must not be persisted')

    fields = {'member': 'reader', 'isbn': '123'}
    fields[field] = value

    with pytest.raises(LoanInputError) as error:
        lend_loan(fields['member'], fields['isbn'], Repository(), FixedClock())

    label = 'ISBN' if field == 'isbn' else 'Member'
    assert error.value.field_errors == {field: f'{label} is required.'}


@pytest.mark.django_db
def test_lend_use_case_assigns_the_next_id_and_clock_date():
    loan = lend_loan('reader', '123', LoanRepository(), FixedClock())

    assert loan.id == 'L4'
    assert loan.lent_on == date(2026, 11, 18)


@pytest.mark.django_db
def test_lend_endpoint_creates_a_loan_with_a_fourteen_day_due_date(client, monkeypatch):
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 18))

    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'L4;dee;123;2026-11-18;2026-12-02;\n'
    assert LoanRepository().find('L4').member == 'dee'


@pytest.mark.django_db
@pytest.mark.parametrize(
    'fields',
    [
        {'member': '', 'isbn': '123'},
        {'member': 'reader', 'isbn': ' \t'},
        {'member': '', 'isbn': ''},
        {},
    ],
)
def test_lend_endpoint_rejects_blank_or_missing_required_fields(client, fields):
    initial_count = Loan.objects.count()

    response = client.post('/loans', fields)

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'member and isbn are required\n'
    assert Loan.objects.count() == initial_count


@pytest.mark.django_db
def test_api_routes_reject_unsupported_methods(client):
    lend = client.put('/loans')
    return_loan_response = client.get('/loans/L1/return')
    browser_lend = client.put('/ui/loans/new/')
    browser_return = client.get('/ui/loans/L1/return/')

    assert lend.status_code == 405
    assert lend['Allow'] == 'GET, POST'
    assert return_loan_response.status_code == 405
    assert return_loan_response['Allow'] == 'POST'
    assert browser_lend.status_code == 405
    assert browser_lend['Allow'] == 'GET, POST'
    assert browser_return.status_code == 405
    assert browser_return['Allow'] == 'POST'


@pytest.mark.django_db
def test_return_use_case_rejects_repeated_return_without_replacing_the_date():
    repository = LoanRepository()

    loan = return_loan('L1', repository, FixedClock())

    assert loan.returned_on == date(2026, 11, 18)
    with pytest.raises(LoanAlreadyReturned):
        return_loan('L1', repository, FixedClock(date(2026, 11, 19)))

    assert Loan.objects.get(pk='L1').returned_on == date(2026, 11, 18)


@pytest.mark.django_db
def test_return_use_case_rejects_an_unknown_loan():
    with pytest.raises(LoanNotFound):
        return_loan('unknown', LoanRepository(), FixedClock())


@pytest.mark.django_db(transaction=True)
def test_repository_return_locks_and_persists_the_loan():
    loan = LoanRepository().mark_returned('L1', date(2026, 11, 18))

    assert loan.returned_on == date(2026, 11, 18)
    assert Loan.objects.get(pk='L1').returned_on == date(2026, 11, 18)


@pytest.mark.django_db
def test_return_endpoint_returns_a_loan_and_rejects_repeated_or_unknown_returns(
    client, monkeypatch
):
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 18))

    returned = client.post('/loans/L1/return')
    repeated = client.post('/loans/L1/return')
    unknown = client.post('/loans/unknown/return')

    assert returned.status_code == 200
    assert returned['Content-Type'] == 'text/plain'
    assert returned.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;2026-11-18\n'
    assert repeated.status_code == 409
    assert repeated['Content-Type'] == 'text/plain'
    assert repeated.content.decode() == 'loan already returned\n'
    assert unknown.status_code == 404
    assert unknown['Content-Type'] == 'text/plain'
    assert unknown.content.decode() == 'no such loan\n'
    assert Loan.objects.get(pk='L1').returned_on == date(2026, 11, 18)


@pytest.mark.django_db
def test_browser_catalog_page_renders_loans_and_the_lend_link(client):
    response = client.get('/ui/loans/')

    assert response.status_code == 200
    assert b'Loan L1' in response.content
    assert b'href="/ui/loans/new/"' in response.content


@pytest.mark.django_db
def test_browser_catalog_detail_renders_a_not_found_page(client):
    response = client.get('/ui/loans/unknown/')

    assert response.status_code == 404
    assert b'<h1 class="mb-4 mt-3 text-4xl">Loan not found.</h1>' in response.content


@pytest.mark.django_db
def test_browser_lend_form_renders_field_errors_for_blank_values(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': ' \t', 'isbn': ''},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 400
    assert b'<div id="lend-form">' in response.content
    assert b'<!doctype html>' not in response.content
    assert b'Member is required.' in response.content
    assert b'ISBN is required.' in response.content


@pytest.mark.django_db
def test_full_page_lend_form_renders_field_errors_for_blank_values(client):
    response = client.post('/ui/loans/new/', {'member': 'reader'})

    assert response.status_code == 400
    assert b'<title>Lend a book' in response.content
    assert b'Member is required.' not in response.content
    assert b'ISBN is required.' in response.content
    assert b'name="member" value="reader"' in response.content
    assert b'name="isbn" value=""' in response.content


@pytest.mark.django_db
def test_browser_lend_form_creates_a_loan_with_htmx(client, monkeypatch):
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 18))

    page = client.get('/ui/loans/new/')
    response = client.post(
        '/ui/loans/new/',
        {'member': 'dee', 'isbn': '123'},
        HTTP_HX_REQUEST='true',
    )

    assert page.status_code == 200
    assert b'hx-post="/ui/loans/new/"' in page.content
    assert b'name="member" value=""' in page.content
    assert b'name="isbn" value=""' in page.content
    assert b'role="alert"' not in page.content
    assert response.status_code == 201
    assert b'Loan L4 has been recorded.' in response.content
    assert b'href="/ui/loans/L4/"' in response.content
    assert Loan.objects.get(pk='L4').lent_on == date(2026, 11, 18)


@pytest.mark.django_db
def test_full_page_lend_form_redirects_to_the_new_loan(client, monkeypatch):
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 18))

    response = client.post('/ui/loans/new/', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/L4/'


@pytest.mark.django_db
def test_browser_return_updates_status_and_renders_a_repeated_return_error(client, monkeypatch):
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 18))

    page = client.get('/ui/loans/L1/')
    response = client.post('/ui/loans/L1/return/', HTTP_HX_REQUEST='true')
    repeated = client.post('/ui/loans/L1/return/', HTTP_HX_REQUEST='true')
    repeated_full_page = client.post('/ui/loans/L1/return/')

    assert page.status_code == 200
    assert b'hx-post="/ui/loans/L1/return/"' in page.content
    assert response.status_code == 200
    assert b'Returned Nov 18, 2026.' in response.content
    assert repeated.status_code == 409
    assert (
        b'<p class="text-sm text-[#a94e37]" role="alert">This loan has already been returned.</p>'
    ) in repeated.content
    assert repeated_full_page.status_code == 409
    assert b'This loan has already been returned.' in repeated_full_page.content
    assert b'Nov 18, 2026' in repeated_full_page.content
    assert Loan.objects.get(pk='L1').returned_on == date(2026, 11, 18)


@pytest.mark.django_db
def test_full_page_return_redirects_to_the_returned_loan(client, monkeypatch):
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 18))

    response = client.post('/ui/loans/L1/return/')

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/L1/'
    assert Loan.objects.get(pk='L1').returned_on == date(2026, 11, 18)


@pytest.mark.django_db
def test_browser_return_renders_an_error_for_an_unknown_loan(client):
    response = client.post('/ui/loans/unknown/return/', HTTP_HX_REQUEST='true')

    assert response.status_code == 404
    assert b'<p class="text-sm text-[#a94e37]" role="alert">No such loan.</p>' in response.content
