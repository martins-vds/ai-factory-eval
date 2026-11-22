from dataclasses import dataclass
from datetime import date

import pytest

from src.fees.services import (
    FeeApplication,
    GatewayResponse,
    GatewayUnavailable,
    LoanNotFound,
    PaymentApplication,
)


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
    def today(self):
        return date(2026, 11, 22)


class PaymentGateway:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def charge(self, loan_id):
        self.calls.append(loan_id)
        if self.error:
            raise self.error
        return self.response


@pytest.mark.parametrize(
    ('due_on', 'returned_on', 'expected_days', 'expected_cents'),
    [
        (date(2026, 11, 23), None, 0, 0),
        (date(2026, 11, 20), None, 2, 0),
        (date(2026, 11, 19), None, 3, 25),
        (date(2026, 10, 1), None, 52, 1000),
        (date(2025, 12, 15), date(2026, 1, 3), 19, 475),
    ],
)
def test_fee_application_calculates_late_days_and_capped_cents(
    due_on, returned_on, expected_days, expected_cents
):
    loan = Loan('L1', due_on, returned_on)
    application = FeeApplication(LoanRepository(loan), FixedClock())

    quote = application.calculate('L1')

    assert (quote.days_late, quote.fee_cents) == (expected_days, expected_cents)


def test_fee_application_returns_none_for_an_unknown_loan():
    application = FeeApplication(LoanRepository(None), FixedClock())

    assert application.calculate('missing') is None


def test_payment_application_requires_a_loan_before_calling_gateway():
    gateway = PaymentGateway(GatewayResponse(200, b'charged\n'))
    application = PaymentApplication(LoanRepository(None), gateway)

    with pytest.raises(LoanNotFound):
        application.pay('missing')

    assert gateway.calls == []


@pytest.mark.parametrize(
    ('gateway_status', 'expected_status'),
    [(200, 200), (503, 502)],
)
def test_payment_application_maps_gateway_status(gateway_status, expected_status):
    loan = Loan('L1', date(2026, 11, 22))
    gateway = PaymentGateway(GatewayResponse(gateway_status, b'gateway response\n'))
    application = PaymentApplication(LoanRepository(loan), gateway)

    result = application.pay('L1')

    assert (result.status, result.body) == (expected_status, b'gateway response\n')


def test_payment_application_preserves_interruption_as_gateway_failure_cause():
    interruption = InterruptedError('gateway call interrupted')
    gateway = PaymentGateway(error=interruption)
    application = PaymentApplication(LoanRepository(Loan('L1', date(2026, 11, 22))), gateway)

    with pytest.raises(GatewayUnavailable) as failure:
        application.pay('L1')

    assert failure.value.__cause__ is interruption
