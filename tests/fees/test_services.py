from dataclasses import dataclass
from datetime import date, timedelta

import pytest

from src.fees.services import (
    FeeApplication,
    GatewayResponse,
    InterruptedPayment,
)


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
        self.value = today

    def today(self):
        return self.value


class PaymentGateway:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.charges = []

    def charge(self, loan_id):
        self.charges.append(loan_id)
        if self.error is not None:
            raise self.error
        return self.response


@pytest.mark.parametrize(
    ('late_days', 'expected_cents'),
    [(0, 0), (2, 0), (3, 75), (19, 475), (296, 1000)],
)
def test_fee_calculation_applies_waiver_threshold_and_cap(late_days, expected_cents):
    due_on = date(2026, 1, 1)
    loan = Loan('L1', due_on, returned_on=due_on + timedelta(days=late_days))
    application = FeeApplication(
        LoanRepository(loan),
        FixedClock(date(2027, 1, 1)),
        PaymentGateway(),
    )

    quote = application.calculate_fee('L1')

    assert quote.days_late == late_days
    assert quote.amount_cents == expected_cents


def test_fee_calculation_uses_today_for_unreturned_loans():
    due_on = date(2026, 1, 1)
    application = FeeApplication(
        LoanRepository(Loan('L1', due_on)),
        FixedClock(due_on + timedelta(days=19)),
        PaymentGateway(),
    )

    quote = application.calculate_fee('L1')

    assert quote.days_late == 19
    assert quote.amount_cents == 475


def test_fee_calculation_returns_none_for_unknown_loan():
    application = FeeApplication(LoanRepository(), FixedClock(date(2026, 1, 1)), PaymentGateway())

    assert application.calculate_fee('unknown') is None


def test_payment_requires_an_existing_loan_before_calling_gateway():
    gateway = PaymentGateway(GatewayResponse(200, 'charged\n'))
    application = FeeApplication(LoanRepository(), FixedClock(date(2026, 1, 1)), gateway)

    assert application.pay('unknown') is None
    assert gateway.charges == []


def test_payment_delegates_to_gateway_for_an_existing_loan():
    gateway = PaymentGateway(GatewayResponse(200, 'charged\n'))
    application = FeeApplication(
        LoanRepository(Loan('L1', date(2026, 1, 1))),
        FixedClock(date(2026, 1, 1)),
        gateway,
    )

    result = application.pay('L1')

    assert result == GatewayResponse(200, 'charged\n')
    assert gateway.charges == ['L1']


def test_payment_does_not_swallow_interruption():
    interruption = InterruptedError('request interrupted')
    gateway_error = InterruptedPayment('payment interrupted')
    gateway_error.__cause__ = interruption
    application = FeeApplication(
        LoanRepository(Loan('L1', date(2026, 1, 1))),
        FixedClock(date(2026, 1, 1)),
        PaymentGateway(error=gateway_error),
    )

    with pytest.raises(InterruptedPayment) as raised:
        application.pay('L1')

    assert raised.value.__cause__ is interruption
