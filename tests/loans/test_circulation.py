from dataclasses import dataclass
from datetime import date, timedelta

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


@dataclass
class LoanRecord:
    id: str
    member: str
    isbn: str
    lent_on: date
    returned_on: date | None = None

    @property
    def due_on(self):
        return self.lent_on + timedelta(days=14)


class MemoryLoanRepository:
    def __init__(self, loans=()):
        self.loans = {loan.id: loan for loan in loans}

    def next_id(self):
        return f'L{len(self.loans) + 1}'

    def create(self, **fields):
        loan = LoanRecord(**fields)
        self.loans[loan.id] = loan
        return loan

    def find(self, loan_id):
        return self.loans.get(loan_id)

    def mark_returned(self, loan_id, returned_on):
        loan = self.find(loan_id)
        if loan is None or loan.returned_on is not None:
            return None
        loan.returned_on = returned_on
        return loan


class FixedClock:
    def today(self):
        return date(2026, 11, 18)


def test_lend_creates_a_loan_with_due_date_fourteen_days_later():
    loan = lend_loan(MemoryLoanRepository(), FixedClock(), 'reader', '123')

    assert loan.id == 'L1'
    assert loan.member == 'reader'
    assert loan.isbn == '123'
    assert loan.lent_on == date(2026, 11, 18)
    assert loan.due_on == date(2026, 12, 2)


def test_lend_rejects_missing_or_blank_member_and_isbn_with_field_errors():
    for member, isbn, expected_field in (
        (None, '123', 'member'),
        (' \t', '123', 'member'),
        ('reader', None, 'isbn'),
        ('reader', ' \n', 'isbn'),
    ):
        with pytest.raises(LoanInputError) as error:
            lend_loan(MemoryLoanRepository(), FixedClock(), member, isbn)

        assert expected_field in error.value.field_errors
        assert error.value.field_errors[expected_field] == 'This field is required.'


def test_return_records_the_clock_date():
    repository = MemoryLoanRepository([LoanRecord('L1', 'reader', '123', date(2026, 11, 1))])

    returned = return_loan(repository, FixedClock(), 'L1')

    assert returned.returned_on == date(2026, 11, 18)
    assert repository.find('L1').returned_on == date(2026, 11, 18)


def test_return_rejects_an_already_returned_loan_without_changing_its_date():
    original_return_date = date(2026, 11, 17)
    repository = MemoryLoanRepository(
        [LoanRecord('L1', 'reader', '123', date(2026, 11, 1), original_return_date)]
    )

    with pytest.raises(LoanAlreadyReturned):
        return_loan(repository, FixedClock(), 'L1')

    assert repository.find('L1').returned_on == original_return_date


def test_return_rejects_an_unknown_loan():
    with pytest.raises(LoanNotFound):
        return_loan(MemoryLoanRepository(), FixedClock(), 'missing')


def test_return_rejects_a_concurrent_return_and_keeps_its_date():
    class ConcurrentReturnRepository(MemoryLoanRepository):
        def mark_returned(self, loan_id, returned_on):
            loan = self.find(loan_id)
            loan.returned_on = date(2026, 11, 17)

    repository = ConcurrentReturnRepository([LoanRecord('L1', 'reader', '123', date(2026, 11, 1))])

    with pytest.raises(LoanAlreadyReturned):
        return_loan(repository, FixedClock(), 'L1')

    assert repository.find('L1').returned_on == date(2026, 11, 17)


def test_return_reports_a_loan_deleted_during_the_return_attempt():
    class DeletedLoanRepository(MemoryLoanRepository):
        def mark_returned(self, loan_id, returned_on):
            self.loans.pop(loan_id)

    repository = DeletedLoanRepository([LoanRecord('L1', 'reader', '123', date(2026, 11, 1))])

    with pytest.raises(LoanNotFound):
        return_loan(repository, FixedClock(), 'L1')


@pytest.mark.django_db
def test_lending_endpoint_creates_a_formatted_loan(client, monkeypatch):
    monkeypatch.setattr('src.loans.clock.timezone.localdate', lambda: date(2026, 11, 18))

    response = client.post('/loans', {'member': 'reader', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'L4;reader;123;2026-11-18;2026-12-02;\n'


@pytest.mark.django_db
@pytest.mark.parametrize(
    'form',
    [
        {'member': 'reader'},
        {'isbn': '123'},
        {'member': '', 'isbn': '123'},
        {'member': 'reader', 'isbn': ' \t'},
    ],
)
def test_lending_endpoint_rejects_missing_and_blank_required_fields(client, form):
    response = client.post('/loans', form)

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'member and isbn are required\n'


@pytest.mark.django_db
def test_return_endpoint_persists_the_return_date(client, monkeypatch):
    monkeypatch.setattr('src.loans.clock.timezone.localdate', lambda: date(2026, 11, 18))

    response = client.post('/loans/L1/return')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == ('L1;ana;9780134685991;2026-01-02;2026-01-16;2026-11-18\n')
    assert client.get('/loans/L1').content.decode().endswith(';2026-11-18\n')


@pytest.mark.django_db
def test_return_endpoint_rejects_repeated_returns_without_replacing_the_date(client):
    response = client.post('/loans/L2/return')

    assert response.status_code == 409
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'loan already returned\n'
    assert client.get('/loans/L2').content.decode().endswith(';2026-01-20\n')


@pytest.mark.django_db
def test_return_endpoint_reports_unknown_loan(client):
    response = client.post('/loans/missing/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_browser_lending_page_uses_reading_room_and_htmx(client):
    response = client.get('/ui/loans/new/')

    assert response.status_code == 200
    assert b'Books in good company.' in response.content
    assert b'hx-post="/ui/loans/new/"' in response.content
    assert b'htmx.org@2.0.11' in response.content


@pytest.mark.django_db
def test_browser_lending_page_renders_field_errors_for_blank_values(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': ' \t', 'isbn': '123'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert b'id="error-member"' in response.content
    assert b'This field is required.' in response.content


@pytest.mark.django_db
@pytest.mark.parametrize(
    'form, error_id',
    [
        ({'isbn': '123'}, b'id="error-member"'),
        ({'member': 'reader'}, b'id="error-isbn"'),
    ],
)
def test_browser_lending_page_renders_errors_for_missing_fields(client, form, error_id):
    response = client.post('/ui/loans/new/', form)

    assert response.status_code == 200
    assert error_id in response.content
    assert b'This field is required.' in response.content


@pytest.mark.django_db
def test_browser_lending_redirects_to_collection_after_success(client, monkeypatch):
    monkeypatch.setattr('src.loans.clock.timezone.localdate', lambda: date(2026, 11, 18))

    response = client.post('/ui/loans/new/', {'member': 'reader', 'isbn': '123'})

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/'
    assert b'L4;reader;123;2026-11-18;2026-12-02;' in client.get('/loans').content


@pytest.mark.django_db
def test_browser_htmx_lending_redirects_to_collection(client, monkeypatch):
    monkeypatch.setattr('src.loans.clock.timezone.localdate', lambda: date(2026, 11, 18))

    response = client.post(
        '/ui/loans/new/',
        {'member': 'reader', 'isbn': '123'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert response['HX-Redirect'] == '/ui/loans/'


@pytest.mark.django_db
def test_browser_collection_posts_returns_to_htmx_path(client):
    response = client.get('/ui/loans/')

    assert response.status_code == 200
    assert b'href="/ui/loans/new/"' in response.content
    assert b'hx-post="/ui/loans/L1/return/"' in response.content
    assert b'hx-target="#loan-L1"' in response.content


@pytest.mark.django_db
def test_browser_return_replaces_loan_row_with_return_date(client, monkeypatch):
    monkeypatch.setattr('src.loans.clock.timezone.localdate', lambda: date(2026, 11, 18))

    response = client.post('/ui/loans/L1/return/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'id="loan-L1"' in response.content
    assert b'Returned Nov 18, 2026' in response.content
    assert b'hx-post="/ui/loans/L1/return/"' not in response.content


@pytest.mark.django_db
def test_browser_return_redirects_to_collection_without_htmx(client, monkeypatch):
    monkeypatch.setattr('src.loans.clock.timezone.localdate', lambda: date(2026, 11, 18))

    response = client.post('/ui/loans/L1/return/')

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/'
    assert client.get('/loans/L1').content.decode().endswith(';2026-11-18\n')


@pytest.mark.django_db
def test_browser_repeat_return_renders_error_and_preserves_return_date(client):
    response = client.post('/ui/loans/L2/return/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="alert"' in response.content
    assert b'This loan has already been returned.' in response.content
    assert b'Returned Jan 20, 2026' in response.content


@pytest.mark.django_db
def test_browser_repeat_return_without_htmx_renders_collection_error(client):
    response = client.post('/ui/loans/L2/return/')

    assert response.status_code == 200
    assert b'Books in good company.' in response.content
    assert b'role="alert"' in response.content
    assert b'This loan has already been returned.' in response.content
    assert b'Loan L1' in response.content


@pytest.mark.django_db
def test_browser_detail_not_found_renders_a_library_page(client):
    response = client.get('/ui/loans/missing/')

    assert response.status_code == 404
    assert b'Loan not found' in response.content
    assert b'Back to the collection' in response.content


@pytest.mark.django_db
def test_browser_htmx_return_not_found_renders_an_error_fragment(client):
    response = client.post('/ui/loans/missing/return/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="alert"' in response.content
    assert b'No such loan.' in response.content


@pytest.mark.django_db
def test_browser_return_not_found_renders_a_library_page(client):
    response = client.post('/ui/loans/missing/return/')

    assert response.status_code == 404
    assert b'Loan not found' in response.content
    assert b'Back to the collection' in response.content


@pytest.mark.django_db
def test_return_repository_rolls_back_if_the_updated_loan_cannot_be_loaded(monkeypatch):
    def fail_to_load(self, loan_id):
        raise RuntimeError('load failed')

    with pytest.raises(RuntimeError, match='load failed'), monkeypatch.context() as patch:
        patch.setattr(LoanRepository, 'find', fail_to_load)
        LoanRepository().mark_returned('L1', date(2026, 11, 18))

    assert Loan.objects.get(pk='L1').returned_on is None


@pytest.mark.django_db
def test_api_routes_reject_unsupported_methods(client):
    assert client.put('/loans').headers['Allow'] == 'GET, POST'
    assert client.get('/loans/L1/return').headers['Allow'] == 'POST'


@pytest.mark.django_db
def test_browser_routes_reject_unsupported_methods(client):
    assert client.put('/ui/loans/new/').headers['Allow'] == 'GET, POST'
    assert client.get('/ui/loans/L1/return/').headers['Allow'] == 'POST'
