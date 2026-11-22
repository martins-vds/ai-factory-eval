from dataclasses import dataclass
from datetime import date

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
    def today(self):
        return date(2026, 11, 22)


def fee_for(*, due_on, returned_on=None):
    loan = Loan('L1', due_on, returned_on)
    return FeeApplication(LoanRepository(loan), FixedClock()).calculate_fee('L1')


def test_fee_is_waived_through_two_days_late():
    fee = fee_for(due_on=date(2026, 11, 20))

    assert (fee.late_days, fee.amount_cents) == (2, 0)


def test_fee_is_twenty_five_cents_per_day_after_grace_period():
    fee = fee_for(due_on=date(2026, 11, 19))

    assert (fee.late_days, fee.amount_cents) == (3, 75)


def test_fee_is_capped_at_ten_dollars():
    fee = fee_for(due_on=date(2026, 9, 1))

    assert fee.amount_cents == 1000


def test_early_or_on_time_loan_has_no_late_days():
    fee = fee_for(due_on=date(2026, 11, 23))

    assert (fee.late_days, fee.amount_cents) == (0, 0)


def test_return_date_is_used_instead_of_today_for_fee_calculation():
    fee = fee_for(due_on=date(2026, 11, 19), returned_on=date(2026, 11, 20))

    assert (fee.late_days, fee.amount_cents) == (1, 0)


def test_missing_loan_has_no_fee():
    fee = FeeApplication(LoanRepository(None), FixedClock()).calculate_fee('missing')

    assert fee is None
