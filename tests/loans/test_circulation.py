from dataclasses import dataclass
from datetime import date, timedelta

import pytest

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
        return f"L{len(self.loans) + 1}"

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


def test_return_records_the_clock_date():
    repository = MemoryLoanRepository(
        [LoanRecord('L1', 'reader', '123', date(2026, 11, 1))]
    )

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
    assert response.content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;2026-11-18\n'
    )
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
