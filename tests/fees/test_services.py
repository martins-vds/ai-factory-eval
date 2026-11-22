from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from src.fees.services import LateFeeApplication


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
    def __init__(self, today):
        self._today = today

    def today(self):
        return self._today


def test_fee_is_25_cents_per_day_after_grace_period():
    application = LateFeeApplication(
        LoanRepository(Loan('L1', date(2026, 1, 16))),
        FixedClock(date(2026, 2, 24)),
    )

    quote = application.calculate('L1')

    assert quote.days_late == 39
    assert quote.amount == Decimal('9.75')
