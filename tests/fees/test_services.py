from dataclasses import dataclass
from datetime import date

import pytest

from src.fees.services import FeeApplication, PaymentGatewayFailure


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
        self.current_date = today

    def today(self):
        return self.current_date


class PaymentGateway:
    def __init__(self, result=None, failure=None):
        self.result = result
        self.failure = failure
        self.calls = []

    def charge(self, loan_id):
        self.calls.append(loan_id)
        if self.failure:
            raise self.failure
        return self.result


def fee_application(*loans, today=date(2026, 11, 9), gateway=None):
    return FeeApplication(
        LoanRepository(*loans),
        FixedClock(today),
        gateway or PaymentGateway(),
    )


def test_fee_uses_return_date_instead_of_today():
    loan = Loan('L1', date(2026, 10, 1), date(2026, 10, 4))

    quote = fee_application(loan, today=date(2026, 11, 9)).quote('L1')

    assert quote.late_days == 3
    assert quote.amount_cents == 75


@pytest.mark.parametrize(
    ('today', 'late_days', 'amount_cents'),
    [
        (date(2026, 9, 30), 0, 0),
        (date(2026, 10, 3), 2, 0),
        (date(2026, 10, 4), 3, 75),
        (date(2027, 1, 1), 92, 1000),
    ],
)
def test_fee_applies_grace_period_daily_rate_and_cap(today, late_days, amount_cents):
    quote = fee_application(Loan('L1', date(2026, 10, 1)), today=today).quote('L1')

    assert quote.late_days == late_days
    assert quote.amount_cents == amount_cents


def test_quote_is_missing_for_unknown_loan():
    assert fee_application().quote('unknown') is None


def test_payment_does_not_call_gateway_for_unknown_loan():
    gateway = PaymentGateway()

    outcome = fee_application(gateway=gateway).pay('unknown')

    assert outcome is None
    assert gateway.calls == []


@pytest.mark.parametrize(
    ('gateway_status', 'expected_status'),
    [(200, 200), (503, 502)],
)
def test_payment_maps_gateway_status_and_preserves_response_body(gateway_status, expected_status):
    gateway = PaymentGateway(
        result=type('Response', (), {'status_code': gateway_status, 'body': 'declined\n'})()
    )
    application = fee_application(Loan('L1', date(2026, 10, 1)), gateway=gateway)

    outcome = application.pay('L1')

    assert outcome.status_code == expected_status
    assert outcome.body == 'declined\n'
    assert gateway.calls == ['L1']


def test_payment_maps_io_failure_to_unavailable_response():
    io_error = OSError('connection reset')
    failure = PaymentGatewayFailure('payment gateway unavailable')
    failure.__cause__ = io_error
    application = fee_application(
        Loan('L1', date(2026, 10, 1)),
        gateway=PaymentGateway(failure=failure),
    )

    outcome = application.pay('L1')

    assert outcome.status_code == 502
    assert outcome.body == 'payment gateway unavailable\n'
    assert outcome.failure.__cause__ is io_error


def test_payment_preserves_interruption_as_a_gateway_failure_cause():
    interruption = InterruptedError('request interrupted')
    failure = PaymentGatewayFailure('payment gateway unavailable')
    failure.__cause__ = interruption
    application = fee_application(
        Loan('L1', date(2026, 10, 1)),
        gateway=PaymentGateway(failure=failure),
    )

    outcome = application.pay('L1')

    assert outcome.status_code == 502
    assert outcome.failure.__cause__ is interruption
