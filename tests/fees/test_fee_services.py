from dataclasses import dataclass
from datetime import date

import pytest

from src.fees.services import (
    FeeApplication,
    LoanNotFound,
    PaymentApplication,
    PaymentGatewayInterrupted,
    PaymentGatewayUnavailable,
)


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


class Clock:
    def __init__(self, today):
        self.today_value = today

    def today(self):
        return self.today_value


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
    ('today', 'days_late', 'amount_cents'),
    [
        (date(2026, 1, 16), 0, 0),
        (date(2026, 1, 18), 2, 0),
        (date(2026, 1, 19), 3, 75),
        (date(2026, 2, 24), 39, 975),
        (date(2026, 2, 25), 40, 1000),
        (date(2026, 6, 30), 165, 1000),
    ],
)
def test_fee_for_loan_applies_waiver_daily_rate_and_cap(today, days_late, amount_cents):
    loan = LoanRecord('L1', due_on=date(2026, 1, 16))
    application = FeeApplication(LoanRepository(loan), Clock(today))

    fee = application.fee_for('L1')

    assert fee.days_late == days_late
    assert fee.amount_cents == amount_cents


def test_fee_stops_on_return_date_and_never_counts_days_early():
    loan = LoanRecord(
        'L3',
        due_on=date(2025, 12, 15),
        returned_on=date(2026, 1, 3),
    )
    application = FeeApplication(LoanRepository(loan), Clock(date(2026, 11, 22)))

    fee = application.fee_for('L3')

    assert fee.days_late == 19
    assert fee.amount_cents == 475

    early_loan = LoanRecord(
        'L2',
        due_on=date(2026, 1, 24),
        returned_on=date(2026, 1, 20),
    )
    early_fee = FeeApplication(LoanRepository(early_loan), Clock(date(2026, 11, 22))).fee_for('L2')

    assert early_fee.days_late == 0
    assert early_fee.amount_cents == 0


def test_fee_for_unknown_loan_raises_not_found():
    application = FeeApplication(LoanRepository(None), Clock(date(2026, 11, 22)))

    with pytest.raises(LoanNotFound):
        application.fee_for('L9')


def test_payment_for_unknown_loan_does_not_call_gateway():
    gateway = PaymentGateway(response=object())
    application = PaymentApplication(LoanRepository(None), gateway)

    with pytest.raises(LoanNotFound):
        application.pay('L9')

    assert gateway.calls == []


@pytest.mark.parametrize(
    ('gateway_response', 'status_code', 'body'),
    [
        (('200', 'charged\n'), 200, 'charged\n'),
        (('503', 'declined\n'), 502, 'declined\n'),
    ],
)
def test_payment_maps_gateway_status_and_forwards_response(gateway_response, status_code, body):
    class Response:
        def __init__(self, status, response_body):
            self.status_code = int(status)
            self.body = response_body

    gateway = PaymentGateway(response=Response(*gateway_response))
    application = PaymentApplication(LoanRepository(LoanRecord('L1', date(2026, 1, 16))), gateway)

    result = application.pay('L1')

    assert result.status_code == status_code
    assert result.body == body
    assert gateway.calls == ['L1']


def test_payment_gateway_unavailable_returns_gateway_failure():
    gateway = PaymentGateway(error=PaymentGatewayUnavailable())
    application = PaymentApplication(LoanRepository(LoanRecord('L1', date(2026, 1, 16))), gateway)

    result = application.pay('L1')

    assert result.status_code == 502
    assert result.body == 'payment gateway unavailable\n'


def test_payment_preserves_interrupted_gateway_call():
    interruption = InterruptedError('request interrupted')
    error = PaymentGatewayInterrupted('payment interrupted')
    error.__cause__ = interruption
    gateway = PaymentGateway(error=error)
    application = PaymentApplication(LoanRepository(LoanRecord('L1', date(2026, 1, 16))), gateway)

    with pytest.raises(PaymentGatewayInterrupted) as raised:
        application.pay('L1')

    assert raised.value.__cause__ is interruption
