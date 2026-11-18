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
