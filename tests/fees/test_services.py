from dataclasses import dataclass
from datetime import date, timedelta

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


class Clock:
    def today(self):
        return date(2026, 11, 19)


@pytest.mark.parametrize(
    ('days_late', 'expected_fee_cents'),
    [(2, 0), (3, 75)],
)
def test_fee_is_waived_through_two_days_late_then_charges_the_full_late_days(
    days_late, expected_fee_cents
):
    due_on = date(2026, 1, 16)
    loan = Loan('L1', due_on, returned_on=due_on + timedelta(days=days_late))
    application = FeeApplication(LoanRepository(loan), Clock())

    fee = application.calculate_fee('L1')

    assert (fee.days_late, fee.fee_cents) == (days_late, expected_fee_cents)
