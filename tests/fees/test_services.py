from dataclasses import dataclass
from datetime import date
from decimal import Decimal

import pytest

from src.fees.services import FeeApplication


@dataclass
class FeeLoan:
    id: str
    due_on: date
    returned_on: date | None = None


class LoanRepository:
    def __init__(self, loan):
        self.loan = loan

    def find(self, loan_id):
        return self.loan if self.loan.id == loan_id else None


class FixedClock:
    def today(self):
        return date(2026, 3, 20)


@pytest.mark.parametrize(
    ('due_on', 'returned_on', 'days_late', 'amount'),
    [
        (date(2026, 3, 21), None, 0, Decimal('0.00')),
        (date(2026, 3, 18), None, 2, Decimal('0.00')),
        (date(2026, 3, 17), None, 3, Decimal('0.25')),
        (date(2026, 3, 17), date(2026, 3, 19), 2, Decimal('0.00')),
        (date(2026, 2, 1), None, 47, Decimal('10.00')),
    ],
)
def test_fee_uses_return_date_or_today_with_grace_period_and_cap(
    due_on, returned_on, days_late, amount
):
    loan = FeeLoan('L1', due_on, returned_on)
    application = FeeApplication(LoanRepository(loan), FixedClock())

    fee = application.for_loan('L1')

    assert fee.days_late == days_late
    assert fee.amount == amount


def test_fee_application_returns_none_for_an_unknown_loan():
    application = FeeApplication(LoanRepository(FeeLoan('L1', date(2026, 3, 20))), FixedClock())

    assert application.for_loan('missing') is None
