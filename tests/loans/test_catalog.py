from datetime import date

from src.loans.domain import Loan


def test_due_date_is_fourteen_calendar_days_after_lending():
    loan = Loan(
        id='L1',
        member='ana',
        isbn='9780134685991',
        lent_on=date(2026, 1, 2),
    )

    assert loan.due_on == date(2026, 1, 16)
