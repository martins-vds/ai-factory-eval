from datetime import date, timedelta
from decimal import Decimal

import pytest

from src.fees.services import (
    FeeLoan,
    LateFeeApplication,
    PaymentGatewayInterrupted,
)


class InMemoryLoanRepository:
    def __init__(self, loan):
        self.loan = loan

    def find(self, loan_id):
        return self.loan if self.loan and self.loan.id == loan_id else None


class FixedClock:
    def __init__(self, today):
        self._today = today

    def today(self):
        return self._today


class InMemoryPaymentGateway:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error

    def charge(self, loan_id):
        if self.error:
            raise self.error
        return self.response


@pytest.mark.parametrize(
    ('days_late', 'expected_fee'),
    [(2, Decimal('0.00')), (3, Decimal('0.75')), (50, Decimal('10.00'))],
)
def test_fee_application_calculates_fee_with_injected_repository_and_clock(
    days_late,
    expected_fee,
):
    due_on = date(2026, 11, 6)
    loan = FeeLoan('L1', due_on, None)
    application = LateFeeApplication(
        InMemoryLoanRepository(loan),
        FixedClock(due_on + timedelta(days=days_late)),
        InMemoryPaymentGateway(),
    )

    fee = application.fee('L1')

    assert fee.days_late == days_late
    assert fee.amount == expected_fee


def test_payment_application_keeps_interruption_cause_and_maps_to_gateway_failure():
    interruption = InterruptedError('request interrupted')
    gateway_error = PaymentGatewayInterrupted('request interrupted')
    gateway_error.__cause__ = interruption
    loan = FeeLoan('L1', date(2026, 11, 6), None)
    application = LateFeeApplication(
        InMemoryLoanRepository(loan),
        FixedClock(date(2026, 11, 9)),
        InMemoryPaymentGateway(error=gateway_error),
    )

    result = application.pay('L1')

    assert result.status_code == 502
    assert result.body == b'payment gateway unavailable\n'
    assert isinstance(result.failure.__cause__, InterruptedError)
