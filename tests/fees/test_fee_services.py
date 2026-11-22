from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

import pytest

from src.fees.services import LateFeeApplication, LoanNotFound


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


def test_late_fee_is_25_cents_per_day_after_grace_period():
    application = LateFeeApplication(
        LoanRepository(Loan('L1', date(2026, 1, 16))),
        FixedClock(date(2026, 2, 24)),
    )

    quote = application.calculate('L1')

    assert quote.days_late == 39
    assert quote.amount == Decimal('9.75')


@pytest.mark.parametrize(
    ('late_days', 'amount'),
    [
        (0, '0.00'),
        (2, '0.00'),
        (3, '0.75'),
        (39, '9.75'),
        (40, '10.00'),
        (165, '10.00'),
    ],
)
def test_fee_waiver_daily_rate_and_cap(late_days, amount):
    application = LateFeeApplication(
        LoanRepository(Loan('L1', date(2026, 1, 16))),
        FixedClock(date(2026, 1, 16) + timedelta(days=late_days)),
    )

    quote = application.calculate('L1')

    assert quote.days_late == late_days
    assert quote.amount == Decimal(amount)


def test_returned_loan_fee_ends_on_return_date():
    application = LateFeeApplication(
        LoanRepository(Loan('L3', date(2025, 12, 15), date(2026, 1, 3))),
        FixedClock(date(2026, 11, 22)),
    )

    quote = application.calculate('L3')

    assert quote.days_late == 19
    assert quote.amount == Decimal('4.75')


def test_fee_rejects_an_unknown_loan():
    application = LateFeeApplication(LoanRepository(), FixedClock(date(2026, 1, 16)))

    with pytest.raises(LoanNotFound):
        application.calculate('L9')
