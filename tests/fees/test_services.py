from dataclasses import dataclass
from datetime import date

import pytest

from src.fees.services import FeeApplication


@dataclass(frozen=True)
class Loan:
    due_on: date
    returned_on: date | None = None


class LoanRepository:
    def __init__(self, loan):
        self.loan = loan

    def find(self, loan_id):
        return self.loan


class FixedClock:
    def __init__(self, today):
        self._today = today

    def today(self):
        return self._today


@pytest.mark.parametrize(
    ('loan', 'today', 'days_late', 'amount_cents'),
    [
        (Loan(date(2026, 1, 5)), date(2026, 1, 3), 0, 0),
        (Loan(date(2026, 1, 1)), date(2026, 1, 3), 2, 0),
        (Loan(date(2026, 1, 1)), date(2026, 1, 4), 3, 75),
        (Loan(date(2026, 1, 1)), date(2026, 1, 20), 19, 475),
        (Loan(date(2026, 1, 1), date(2026, 1, 4)), date(2026, 2, 1), 3, 75),
        (Loan(date(2026, 1, 1)), date(2026, 3, 1), 59, 1000),
    ],
)
def test_late_fee_uses_return_date_grace_period_and_cap(loan, today, days_late, amount_cents):
    application = FeeApplication(LoanRepository(loan), FixedClock(today))

    quote = application.quote_for('L3')

    assert quote.days_late == days_late
    assert quote.amount_cents == amount_cents
