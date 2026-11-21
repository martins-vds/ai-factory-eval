from datetime import date

import pytest

from src.loans.domain import Loan
from src.loans.services import ExportLoans, GetLoan, ListLoans, LoanNotFound


class StubLoanRepository:
    def __init__(self, loans):
        self.loans = loans

    def list_all(self):
        return self.loans

    def get(self, loan_id):
        return next((loan for loan in self.loans if loan.id == loan_id), None)


def test_list_loans_returns_records_in_id_order():
    repository = StubLoanRepository(
        [
            Loan('L3', 'cy', '9781617294945', date(2025, 12, 1), date(2026, 1, 3)),
            Loan('L1', 'ana', '9780134685991', date(2026, 1, 2), None),
        ]
    )

    loans = ListLoans(repository).execute()

    assert [loan.id for loan in loans] == ['L1', 'L3']


def test_due_date_is_fourteen_calendar_days_after_lending():
    loan = Loan('L1', 'ana', '9780134685991', date(2024, 2, 24), None)

    assert loan.due_on == date(2024, 3, 9)


def test_get_loan_rejects_an_unknown_id():
    with pytest.raises(LoanNotFound):
        GetLoan(StubLoanRepository([])).execute('missing')


def test_export_quotes_delimiters_and_preserves_a_round_trippable_record():
    loan = Loan('L9', 'a;b', '123;456', date(2026, 3, 1), None)
    repository = StubLoanRepository([loan])

    assert ExportLoans(repository).execute() == ('L9;"a;b";"123;456";2026-03-01;2026-03-15;\n')
