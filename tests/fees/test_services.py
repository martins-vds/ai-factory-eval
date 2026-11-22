from dataclasses import dataclass
from datetime import date

import pytest

from src.fees.services import FeeApplication


@dataclass
class LoanRecord:
    id: str
    due_on: date
    returned_on: date | None = None


class LoanRepository:
    def __init__(self, loan):
        self.loan = loan

    def find(self, loan_id):
        return self.loan if self.loan and self.loan.id == loan_id else None


class Clock:
    def __init__(self, today):
        self.today_value = today

    def today(self):
        return self.today_value


@pytest.mark.parametrize(
    ('today', 'days_late', 'amount_cents'),
    [
        (date(2026, 1, 16), 0, 0),
        (date(2026, 1, 18), 2, 0),
        (date(2026, 1, 19), 3, 75),
        (date(2026, 2, 24), 39, 975),
        (date(2026, 2, 25), 40, 1000),
        (date(2026, 6, 30), 165, 1000),
    ],
)
def test_fee_for_loan_applies_waiver_daily_rate_and_cap(today, days_late, amount_cents):
    loan = LoanRecord('L1', due_on=date(2026, 1, 16))
    application = FeeApplication(LoanRepository(loan), Clock(today))

    fee = application.fee_for('L1')

    assert fee.days_late == days_late
    assert fee.amount_cents == amount_cents
