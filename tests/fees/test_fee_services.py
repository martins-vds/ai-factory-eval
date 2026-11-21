from dataclasses import dataclass
from datetime import date
from decimal import Decimal

import pytest

from src.fees.services import FeeApplication, GatewayResponse, PaymentApplication


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
    def __init__(self, today=date(2026, 1, 4)):
        self._today = today

    def today(self):
        return self._today


class PaymentGateway:
    def __init__(self, response=None, failure=None):
        self.calls = []
        self.response = response
        self.failure = failure

    def charge(self, loan_id):
        self.calls.append(loan_id)
        if self.failure is not None:
            raise self.failure
        return self.response


def test_fee_application_charges_daily_fee_after_the_two_day_grace_period():
    loan = Loan('L1', due_on=date(2026, 1, 1))
    application = FeeApplication(LoanRepository(loan), FixedClock())

    fee = application.fee_for('L1')

    assert fee.late_days == 3
    assert fee.amount == Decimal('0.75')


def test_fee_for_unknown_loan_returns_no_quote():
    application = FeeApplication(LoanRepository(None), FixedClock())

    assert application.fee_for('missing') is None


def test_fee_uses_return_date_and_clamps_early_returns_to_zero():
    loan = Loan('L1', due_on=date(2026, 1, 1), returned_on=date(2025, 12, 31))
    application = FeeApplication(LoanRepository(loan), FixedClock())

    fee = application.fee_for('L1')

    assert fee.late_days == 0
    assert fee.amount == Decimal('0.00')


@pytest.mark.parametrize(
    ('today', 'late_days', 'amount'),
    [
        (date(2026, 1, 3), 2, Decimal('0.00')),
        (date(2026, 1, 4), 3, Decimal('0.75')),
        (date(2026, 3, 2), 60, Decimal('10.00')),
    ],
)
def test_fee_for_loan_observes_grace_period_and_cap(today, late_days, amount):
    loan = Loan('L1', due_on=date(2026, 1, 1))
    application = FeeApplication(LoanRepository(loan), FixedClock(today))

    fee = application.fee_for('L1')

    assert fee.late_days == late_days
    assert fee.amount == amount


def test_payment_for_unknown_loan_does_not_call_gateway():
    gateway = PaymentGateway()
    application = PaymentApplication(LoanRepository(None), gateway)

    result = application.pay('missing')

    assert result is None
    assert gateway.calls == []


@pytest.mark.parametrize(
    ('gateway_status', 'expected_status'),
    [(200, 200), (503, 502)],
)
def test_payment_maps_gateway_status_and_preserves_response_body(gateway_status, expected_status):
    loan = Loan('L1', due_on=date(2026, 1, 1))
    gateway = PaymentGateway(GatewayResponse(gateway_status, 'charged\n'))
    application = PaymentApplication(LoanRepository(loan), gateway)

    result = application.pay('L1')

    assert result.status_code == expected_status
    assert result.body == 'charged\n'
    assert gateway.calls == ['L1']


def test_interrupted_payment_is_a_gateway_failure_and_retains_interruption():
    interruption = InterruptedError('request interrupted')
    loan = Loan('L1', due_on=date(2026, 1, 1))
    gateway = PaymentGateway(failure=interruption)
    application = PaymentApplication(LoanRepository(loan), gateway)

    result = application.pay('L1')

    assert result.status_code == 502
    assert result.body == 'payment gateway unavailable\n'
    assert result.interruption is interruption


def test_gateway_io_failure_becomes_a_502_payment_result():
    loan = Loan('L1', due_on=date(2026, 1, 1))
    gateway = PaymentGateway(failure=OSError('connection refused'))
    application = PaymentApplication(LoanRepository(loan), gateway)

    result = application.pay('L1')

    assert result.status_code == 502
    assert result.body == 'payment gateway unavailable\n'
