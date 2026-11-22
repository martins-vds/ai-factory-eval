from datetime import date

from src.loans.domain import Loan
from src.loans.services import loan_due_date


def test_due_date_is_fourteen_calendar_days_after_lending():
    loan = Loan(
        id='L1',
        member='ana',
        isbn='9780134685991',
        lent_on=date(2026, 1, 2),
        returned_on=None,
    )

    assert loan_due_date(loan) == date(2026, 1, 16)
