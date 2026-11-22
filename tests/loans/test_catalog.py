from datetime import date

from src.loans.domain import Loan
from src.loans.services import format_loan, get_loan, list_loans


class LoanReader:
    def __init__(self, loans):
        self.loans = loans

    def list(self):
        return self.loans

    def get(self, loan_id):
        return next((loan for loan in self.loans if loan.id == loan_id), None)


def test_list_loans_orders_records_by_id():
    reader = LoanReader(
        [
            Loan('L3', 'cy', 'isbn-c', date(2026, 1, 3), None),
            Loan('L1', 'ana', 'isbn-a', date(2026, 1, 1), None),
            Loan('L2', 'bo', 'isbn-b', date(2026, 1, 2), None),
        ]
    )

    assert [loan.id for loan in list_loans(reader)] == ['L1', 'L2', 'L3']


def test_format_loan_escapes_delimiters_and_keeps_trailing_newline():
    loan = Loan('L4', 'a;b', '123;456', date(2026, 1, 2), None)

    assert format_loan(loan) == 'L4;"a;b";"123;456";2026-01-02;2026-01-16;\n'


def test_get_loan_returns_none_when_id_is_unknown():
    assert get_loan(LoanReader([]), 'missing') is None
