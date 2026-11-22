from dataclasses import dataclass
from datetime import date

from src.fees.services import FeeApplication


@dataclass
class Loan:
    id: str
    due_on: date
    returned_on: date | None = None


class LoanRepository:
    def __init__(self, *loans):
        self.loans = {loan.id: loan for loan in loans}

    def find(self, loan_id):
        return self.loans.get(loan_id)


class FixedClock:
    def today(self):
        return date(2026, 1, 19)


def test_fee_calculation_charges_twenty_five_cents_after_two_day_grace_period():
    application = FeeApplication(
        LoanRepository(Loan('L1', date(2026, 1, 16))),
        FixedClock(),
    )

    fee = application.calculate('L1')

    assert fee.days_late == 3
    assert fee.amount_cents == 75
