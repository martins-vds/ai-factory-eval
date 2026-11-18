from dataclasses import dataclass
from datetime import date, timedelta

import pytest

from src.fees.gateway import HttpPaymentGateway
from src.fees.services import FeeApplication, PaymentGatewayError


@dataclass
class LoanRecord:
    id: str
    due_on: date
    returned_on: date | None = None


class LoanRepository:
    def __init__(self, loan):
        self.loan = loan

    def find(self, loan_id):
        return self.loan if self.loan and self.loan.id == loan_id else None

    def all(self):
        return [self.loan] if self.loan else []


class FixedClock:
    def __init__(self, today):
        self.value = today

    def today(self):
        return self.value


@pytest.mark.parametrize(
    ('late_days', 'amount_cents'),
    [(0, 0), (2, 0), (3, 75), (40, 1000), (41, 1000)],
)
def test_fee_calculation_applies_grace_period_and_cap(late_days, amount_cents):
    due_on = date(2026, 1, 1)
    loan = LoanRecord('L1', due_on)
    fees = FeeApplication(
        LoanRepository(loan),
        FixedClock(due_on + timedelta(days=late_days)),
    )

    fee = fees.calculate('L1')

    assert fee.late_days == late_days
    assert fee.amount_cents == amount_cents


def test_fee_calculation_uses_return_date_instead_of_today():
    due_on = date(2026, 1, 1)
    loan = LoanRecord('L1', due_on, returned_on=due_on + timedelta(days=3))
    fees = FeeApplication(LoanRepository(loan), FixedClock(due_on + timedelta(days=30)))

    fee = fees.calculate('L1')

    assert fee.late_days == 3
    assert fee.amount_cents == 75


def test_fee_calculation_returns_none_for_unknown_loan():
    fees = FeeApplication(LoanRepository(None), FixedClock(date(2026, 1, 1)))

    assert fees.calculate('missing') is None


def test_gateway_failure_retains_interruption():
    class InterruptingOpener:
        def open(self, request):
            raise InterruptedError('payment request interrupted')

    gateway = HttpPaymentGateway(base_url='http://payments.invalid', opener=InterruptingOpener())

    with pytest.raises(PaymentGatewayError) as failure:
        gateway.charge('L1')

    assert isinstance(failure.value.__cause__, InterruptedError)
