from datetime import date

import pytest

from src.loans.domain import Loan


class InMemoryLoanRepository:
    def __init__(self, loans):
        self.loans = loans

    def all(self):
        return self.loans

    def find(self, loan_id):
        return next((loan for loan in self.loans if loan.id == loan_id), None)


def test_due_date_is_fourteen_calendar_days_after_lending():
    loan = Loan(
        id='L1',
        member='ana',
        isbn='9780134685991',
        lent_on=date(2026, 1, 2),
    )

    assert loan.due_on == date(2026, 1, 16)


def test_list_loans_are_ordered_by_id():
    from src.loans.services import list_loans

    loans = [
        Loan(id='L2', member='bo', isbn='2', lent_on=date(2026, 1, 10)),
        Loan(id='L1', member='ana', isbn='1', lent_on=date(2026, 1, 2)),
    ]

    assert [loan.id for loan in list_loans(InMemoryLoanRepository(loans))] == ['L1', 'L2']


def test_get_returns_none_when_loan_is_missing():
    from src.loans.services import get_loan

    assert get_loan(InMemoryLoanRepository([]), 'missing') is None


def test_export_escapes_delimiters_and_line_breaks():
    from src.loans.services import export_loans

    loan = Loan(
        id='L1',
        member='a;b',
        isbn='123\n456',
        lent_on=date(2026, 1, 2),
    )

    assert export_loans(InMemoryLoanRepository([loan])) == (
        'L1;"a;b";"123\n456";2026-01-02;2026-01-16;\n'
    )


def test_empty_export_retains_the_trailing_newline():
    from src.loans.services import export_loans

    assert export_loans(InMemoryLoanRepository([])) == '\n'


@pytest.mark.django_db
def test_list_api_returns_seeded_records_as_plain_text(client):
    response = client.get('/loans')

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
        'L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03\n'
    )


@pytest.mark.django_db
def test_get_api_returns_known_record_as_plain_text(client):
    response = client.get('/loans/L1')

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'


@pytest.mark.django_db
def test_get_api_returns_legacy_not_found_response(client):
    response = client.get('/loans/missing')

    assert response.status_code == 404
    assert response.headers['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_repository_commits_loan_writes_and_recovers_from_a_failed_write():
    from django.db import IntegrityError

    from src.loans.repositories import DjangoLoanRepository

    repository = DjangoLoanRepository()
    loan = Loan(id='L4', member='dee', isbn='123', lent_on=date(2026, 11, 22))

    assert repository.create(loan) == loan
    with pytest.raises(IntegrityError):
        repository.create(Loan(id='L4', member='other', isbn='456', lent_on=date(2026, 11, 23)))

    assert repository.find('L4') == loan


@pytest.mark.django_db
def test_reapplying_startup_migrations_does_not_overwrite_existing_loans():
    from django.core.management import call_command

    from src.loans.models import LoanRecord

    LoanRecord.objects.filter(pk='L1').update(member='preserved member')

    call_command('migrate', interactive=False, verbosity=0)

    assert LoanRecord.objects.get(pk='L1').member == 'preserved member'
