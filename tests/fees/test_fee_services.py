from dataclasses import dataclass
from datetime import date

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
        return self.loan if self.loan and self.loan.id == loan_id else None


class FixedClock:
    def today(self):
        return date(2026, 11, 22)


def test_late_fee_is_waived_through_two_days_late():
    loan = FeeLoan('L1', due_on=date(2026, 11, 20))
    application = FeeApplication(LoanRepository(loan), FixedClock())

    quote = application.calculate('L1')

    assert quote.days_late == 2
    assert quote.amount_cents == 0


def test_late_fee_charges_all_late_days_after_the_waiver():
    loan = FeeLoan('L1', due_on=date(2026, 11, 19))
    application = FeeApplication(LoanRepository(loan), FixedClock())

    quote = application.calculate('L1')

    assert quote.days_late == 3
    assert quote.amount_cents == 75


def test_late_fee_uses_return_date_instead_of_today():
    loan = FeeLoan('L1', due_on=date(2026, 11, 8), returned_on=date(2026, 11, 10))
    application = FeeApplication(LoanRepository(loan), FixedClock())

    quote = application.calculate('L1')

    assert quote.days_late == 2
    assert quote.amount_cents == 0


def test_early_return_has_no_late_days_or_fee():
    loan = FeeLoan('L1', due_on=date(2026, 11, 24), returned_on=date(2026, 11, 20))
    application = FeeApplication(LoanRepository(loan), FixedClock())

    quote = application.calculate('L1')

    assert quote.days_late == 0
    assert quote.amount_cents == 0


def test_late_fee_is_capped_at_ten_dollars():
    loan = FeeLoan('L1', due_on=date(2026, 10, 1))
    application = FeeApplication(LoanRepository(loan), FixedClock())

    quote = application.calculate('L1')

    assert quote.days_late == 52
    assert quote.amount_cents == 1000


def test_missing_loan_has_no_late_fee():
    application = FeeApplication(LoanRepository(None), FixedClock())

    assert application.calculate('missing') is None
