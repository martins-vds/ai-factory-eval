from dataclasses import dataclass
from datetime import date

import pytest

from src.fees.services import LateFeeApplication


@dataclass
class Loan:
    id: str
    due_on: date
    returned_on: date | None = None


class LoanRepository:
    def __init__(self, loan):
        self.loan = loan

    def find(self, loan_id):
        return self.loan if self.loan and self.loan.id == loan_id else None


class FixedClock:
    def __init__(self, today):
        self.current_date = today

    def today(self):
        return self.current_date


@pytest.mark.parametrize(
    ('actual_on', 'late_days', 'amount_cents'),
    [
        (date(2026, 3, 10), 0, 0),
        (date(2026, 3, 12), 2, 0),
        (date(2026, 3, 13), 3, 75),
        (date(2026, 4, 22), 42, 1000),
    ],
)
def test_late_fee_uses_two_day_grace_and_caps_at_ten_dollars(
    actual_on, late_days, amount_cents
):
    loan = Loan('L1', date(2026, 3, 10))
    application = LateFeeApplication(LoanRepository(loan), FixedClock(actual_on))

    fee = application.calculate('L1')

    assert fee.loan_id == 'L1'
    assert fee.due_on == date(2026, 3, 10)
    assert fee.late_days == late_days
    assert fee.amount_cents == amount_cents


def test_return_date_takes_precedence_over_the_current_date():
    loan = Loan('L1', date(2026, 3, 10), returned_on=date(2026, 3, 12))
    application = LateFeeApplication(LoanRepository(loan), FixedClock(date(2026, 4, 22)))

    fee = application.calculate('L1')

    assert fee.late_days == 2
    assert fee.amount_cents == 0


def test_late_fee_is_missing_when_loan_does_not_exist():
    application = LateFeeApplication(LoanRepository(None), FixedClock(date(2026, 3, 10)))

    assert application.calculate('missing') is None
