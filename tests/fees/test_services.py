from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

import pytest

from src.fees.services import FeeApplication


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
        self.current_day = today

    def today(self):
        return self.current_day


@pytest.mark.parametrize(
    ('late_days', 'amount'),
    [
        (0, Decimal('0.00')),
        (2, Decimal('0.00')),
        (3, Decimal('0.25')),
        (42, Decimal('10.00')),
        (60, Decimal('10.00')),
    ],
)
def test_late_fee_applies_grace_period_daily_rate_and_cap(late_days, amount):
    due_on = date(2026, 1, 1)
    loan = Loan('L1', due_on)
    application = FeeApplication(
        LoanRepository(loan),
        FixedClock(due_on + timedelta(days=late_days)),
    )

    fee = application.calculate('L1')

    assert fee.late_days == late_days
    assert fee.amount == amount


def test_late_fee_uses_return_date_instead_of_today_and_never_goes_negative():
    due_on = date(2026, 1, 1)
    loan = Loan('L1', due_on, returned_on=due_on - timedelta(days=1))
    application = FeeApplication(
        LoanRepository(loan),
        FixedClock(due_on + timedelta(days=10)),
    )

    fee = application.calculate('L1')

    assert fee.late_days == 0
    assert fee.amount == Decimal('0.00')


def test_fee_calculation_returns_none_for_an_unknown_loan():
    application = FeeApplication(LoanRepository(None), FixedClock(date(2026, 1, 1)))

    assert application.calculate('unknown') is None
