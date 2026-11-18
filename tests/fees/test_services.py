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
        return self.loan if loan_id == self.loan.id else None


class Clock:
    def today(self):
        return date(2026, 11, 10)


def test_fee_starts_at_twenty_five_cents_per_day_after_grace_period():
    loan = Loan(id='L1', due_on=date(2026, 11, 7))
    application = FeeApplication(LoanRepository(loan), Clock())

    fee = application.calculate('L1')

    assert fee.loan_id == 'L1'
    assert fee.due_on == date(2026, 11, 7)
    assert fee.days_late == 3
    assert fee.amount_cents == 75


def test_fee_is_waived_through_two_days_and_capped_at_ten_dollars():
    repository = LoanRepository(Loan(id='L1', due_on=date(2026, 11, 8)))
    application = FeeApplication(repository, Clock())

    two_days_late = application.calculate('L1')
    repository.loan = Loan(id='L1', due_on=date(2026, 11, 7))
    three_days_late = application.calculate('L1')
    repository.loan = Loan(id='L1', due_on=date(2026, 9, 1))
    capped = application.calculate('L1')

    assert two_days_late.days_late == 2
    assert two_days_late.amount_cents == 0
    assert three_days_late.amount_cents == 75
    assert capped.amount_cents == 1000


def test_fee_uses_return_date_and_never_charges_for_early_returns():
    returned_loan = Loan(
        id='L1',
        due_on=date(2026, 11, 7),
        returned_on=date(2026, 11, 8),
    )
    application = FeeApplication(LoanRepository(returned_loan), Clock())

    returned_fee = application.calculate('L1')

    assert returned_fee.days_late == 1
    assert returned_fee.amount_cents == 0

    early_loan = Loan(id='L2', due_on=date(2026, 11, 11))
    application = FeeApplication(LoanRepository(early_loan), Clock())

    early_fee = application.calculate('L2')

    assert early_fee.days_late == 0
    assert early_fee.amount_cents == 0


def test_fee_application_returns_none_for_an_unknown_loan():
    application = FeeApplication(LoanRepository(Loan(id='L1', due_on=date(2026, 11, 7))), Clock())

    assert application.calculate('unknown') is None
