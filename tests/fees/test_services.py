from dataclasses import dataclass
from datetime import date
from decimal import Decimal

import pytest

from src.fees.services import (
    FeeApplication,
    GatewayResponse,
    PaymentApplication,
    PaymentInterrupted,
)


@dataclass
class FeeLoan:
    id: str
    due_on: date
    returned_on: date | None = None


class LoanRepository:
    def __init__(self, loan):
        self.loan = loan

    def find(self, loan_id):
        return self.loan if self.loan.id == loan_id else None


class FixedClock:
    def today(self):
        return date(2026, 3, 20)


class PaymentGateway:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.charged_loans = []

    def charge(self, loan_id):
        self.charged_loans.append(loan_id)
        if self.error is not None:
            raise self.error
        return self.response


@pytest.mark.parametrize(
    ('due_on', 'returned_on', 'days_late', 'amount'),
    [
        (date(2026, 3, 21), None, 0, Decimal('0.00')),
        (date(2026, 3, 18), None, 2, Decimal('0.00')),
        (date(2026, 3, 17), None, 3, Decimal('0.75')),
        (date(2026, 3, 17), date(2026, 3, 19), 2, Decimal('0.00')),
        (date(2026, 2, 1), None, 47, Decimal('10.00')),
    ],
)
def test_fee_uses_return_date_or_today_with_grace_period_and_cap(
    due_on, returned_on, days_late, amount
):
    loan = FeeLoan('L1', due_on, returned_on)
    application = FeeApplication(LoanRepository(loan), FixedClock())

    fee = application.for_loan('L1')

    assert fee.days_late == days_late
    assert fee.amount == amount


def test_fee_application_returns_none_for_an_unknown_loan():
    application = FeeApplication(LoanRepository(FeeLoan('L1', date(2026, 3, 20))), FixedClock())

    assert application.for_loan('missing') is None


def test_payment_application_returns_successful_gateway_response():
    gateway = PaymentGateway(GatewayResponse(200, b'charged\n'))
    application = PaymentApplication(LoanRepository(FeeLoan('L1', date(2026, 3, 20))), gateway)

    result = application.pay('L1')

    assert (result.status, result.body) == (200, b'charged\n')
    assert gateway.charged_loans == ['L1']


def test_payment_application_does_not_charge_an_unknown_loan():
    gateway = PaymentGateway(GatewayResponse(200, b'charged\n'))
    application = PaymentApplication(LoanRepository(FeeLoan('L1', date(2026, 3, 20))), gateway)

    assert application.pay('missing') is None
    assert gateway.charged_loans == []


def test_payment_application_maps_declines_to_gateway_failure():
    gateway = PaymentGateway(GatewayResponse(503, b'declined\n'))
    application = PaymentApplication(LoanRepository(FeeLoan('L1', date(2026, 3, 20))), gateway)

    result = application.pay('L1')

    assert (result.status, result.body) == (502, b'declined\n')


def test_payment_application_maps_io_failure_to_unavailable_response():
    gateway = PaymentGateway(error=OSError('offline'))
    application = PaymentApplication(LoanRepository(FeeLoan('L1', date(2026, 3, 20))), gateway)

    result = application.pay('L1')

    assert (result.status, result.body) == (502, b'payment gateway unavailable\n')


def test_payment_application_preserves_an_interrupted_gateway_call():
    gateway = PaymentGateway(error=InterruptedError('interrupted'))
    application = PaymentApplication(LoanRepository(FeeLoan('L1', date(2026, 3, 20))), gateway)

    with pytest.raises(PaymentInterrupted) as interrupted:
        application.pay('L1')

    assert isinstance(interrupted.value.__cause__, InterruptedError)
