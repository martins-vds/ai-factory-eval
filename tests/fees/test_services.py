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
    def __init__(self, *loans):
        self.loans = {loan.id: loan for loan in loans}

    def find(self, loan_id):
        return self.loans.get(loan_id)


class FixedClock:
    def __init__(self, today):
        self.current_date = today

    def today(self):
        return self.current_date


@pytest.mark.parametrize(
    ('due_on', 'returned_on', 'today', 'late_days', 'amount'),
    [
        (date(2026, 1, 2), None, date(2026, 1, 1), 0, Decimal('0.00')),
        (date(2026, 1, 1), None, date(2026, 1, 3), 2, Decimal('0.00')),
        (date(2026, 1, 1), None, date(2026, 1, 4), 3, Decimal('0.75')),
        (date(2026, 1, 1), None, date(2026, 5, 1), 120, Decimal('10.00')),
        (date(2026, 1, 1), date(2026, 1, 2), date(2026, 5, 1), 1, Decimal('0.00')),
    ],
)
def test_fee_calculation_matches_characterized_days_grace_rate_and_cap(
    due_on, returned_on, today, late_days, amount
):
    application = FeeApplication(
        LoanRepository(FeeLoan('L1', due_on, returned_on)),
        FixedClock(today),
        gateway=None,
    )

    quote = application.fee_for('L1')

    assert quote.late_days == late_days
    assert quote.amount == amount
