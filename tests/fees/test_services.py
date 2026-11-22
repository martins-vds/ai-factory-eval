from dataclasses import dataclass
from datetime import date, timedelta

import pytest

from src.fees.services import FeeApplication, PaymentApplication


@dataclass
class LoanRecord:
    id: str
    due_on: date
    returned_on: date | None = None


class LoanRepository:
    def __init__(self, loan=None):
        self.loan = loan

    def find(self, loan_id):
        return self.loan if self.loan and self.loan.id == loan_id else None


class FixedClock:
    def __init__(self, today):
        self.current_date = today

    def today(self):
        return self.current_date


class PaymentGateway:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.loan_ids = []

    def charge(self, loan_id):
        self.loan_ids.append(loan_id)
        if self.error:
            raise self.error
        return self.response


@pytest.mark.parametrize(
    ('late_days', 'expected_cents'),
    [(0, 0), (1, 0), (2, 0), (3, 75), (40, 1000), (296, 1000)],
)
def test_fee_calculation_waives_at_most_two_days_then_charges_and_caps(late_days, expected_cents):
    due_on = date(2026, 1, 1)
    application = FeeApplication(
        LoanRepository(LoanRecord('L1', due_on)),
        FixedClock(due_on + timedelta(days=late_days)),
    )

    fee = application.calculate('L1')

    assert fee.late_days == late_days
    assert fee.amount_cents == expected_cents


def test_fee_calculation_uses_return_date_and_returns_no_fee_for_unknown_loan():
    today = date(2026, 3, 1)
    loan = LoanRecord('L1', today - timedelta(days=20), today - timedelta(days=19))
    application = FeeApplication(LoanRepository(loan), FixedClock(today))

    fee = application.calculate('L1')
    missing = application.calculate('unknown')

    assert fee.late_days == 1
    assert fee.amount_cents == 0
    assert missing is None


def test_payment_requires_an_existing_loan_before_calling_gateway():
    gateway = PaymentGateway()
    application = PaymentApplication(LoanRepository(), gateway)

    result = application.pay('unknown')

    assert (result.status, result.body) == (404, b'no such loan\n')
    assert gateway.loan_ids == []


@pytest.mark.parametrize(
    ('gateway_status', 'gateway_body', 'expected_status'),
    [(200, b'charged\n', 200), (503, b'declined\n', 502)],
)
def test_payment_maps_gateway_status_and_preserves_its_response_body(
    gateway_status, gateway_body, expected_status
):
    gateway = PaymentGateway(response=type('Response', (), {'status': gateway_status, 'body': gateway_body})())
    application = PaymentApplication(LoanRepository(LoanRecord('L1', date(2026, 1, 1))), gateway)

    result = application.pay('L1')

    assert (result.status, result.body) == (expected_status, gateway_body)
    assert gateway.loan_ids == ['L1']


@pytest.mark.parametrize('error', [OSError('unavailable'), InterruptedError('interrupted')])
def test_payment_maps_transport_failures_to_gateway_unavailable(error):
    gateway = PaymentGateway(error=error)
    application = PaymentApplication(LoanRepository(LoanRecord('L1', date(2026, 1, 1))), gateway)

    result = application.pay('L1')

    assert (result.status, result.body) == (502, b'payment gateway unavailable\n')
    assert result.interruption is (error if isinstance(error, InterruptedError) else None)
