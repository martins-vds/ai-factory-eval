from dataclasses import dataclass
from datetime import date, timedelta

import pytest

from src.fees.services import FeeApplication, PaymentGatewayFailure, PaymentResult


@dataclass
class Loan:
    id: str
    due_on: date
    returned_on: date | None = None


class LoanRepository:
    def __init__(self, loans):
        self.loans = {loan.id: loan for loan in loans}

    def find(self, loan_id):
        return self.loans.get(loan_id)


class Clock:
    def __init__(self, today):
        self.current_date = today

    def today(self):
        return self.current_date


class PaymentGateway:
    def __init__(self, result=None, failure=None):
        self.charges = []
        self.result = result or PaymentResult(200, 'charged\n')
        self.failure = failure

    def charge(self, loan_id):
        self.charges.append(loan_id)
        if self.failure is not None:
            raise self.failure
        return self.result


@pytest.mark.parametrize(
    ('days_late', 'amount_cents'),
    [(0, 0), (1, 0), (2, 0), (3, 75), (40, 1000), (41, 1000)],
)
def test_fee_waiver_daily_rate_and_cap(days_late, amount_cents):
    due_on = date(2026, 10, 12)
    loan = Loan('L1', due_on)
    application = FeeApplication(
        LoanRepository([loan]),
        Clock(due_on + timedelta(days=days_late)),
        PaymentGateway(),
    )

    fee = application.calculate_fee('L1')

    assert fee.days_late == days_late
    assert fee.amount_cents == amount_cents


def test_fee_uses_return_date_instead_of_today():
    due_on = date(2026, 10, 12)
    loan = Loan('L1', due_on, returned_on=due_on + timedelta(days=1))
    application = FeeApplication(
        LoanRepository([loan]),
        Clock(due_on + timedelta(days=20)),
        PaymentGateway(),
    )

    fee = application.calculate_fee('L1')

    assert fee.days_late == 1
    assert fee.amount_cents == 0


def test_fee_for_unknown_loan_is_not_calculated():
    application = FeeApplication(LoanRepository([]), Clock(date(2026, 10, 12)), PaymentGateway())

    assert application.calculate_fee('missing') is None


def test_payment_for_unknown_loan_does_not_call_gateway():
    gateway = PaymentGateway()
    application = FeeApplication(LoanRepository([]), Clock(date(2026, 10, 12)), gateway)

    assert application.pay('missing') is None
    assert gateway.charges == []


@pytest.mark.parametrize(
    ('gateway_status', 'succeeded'),
    [(200, True), (503, False)],
)
def test_payment_only_succeeds_for_gateway_http_200(gateway_status, succeeded):
    loan = Loan('L1', date(2026, 10, 12))
    gateway = PaymentGateway(PaymentResult(gateway_status, 'gateway response'))
    application = FeeApplication(
        LoanRepository([loan]),
        Clock(date(2026, 10, 12)),
        gateway,
    )

    outcome = application.pay('L1')

    assert outcome.succeeded is succeeded
    assert outcome.body == 'gateway response'
    assert gateway.charges == ['L1']


def test_payment_outcome_keeps_interrupted_failure_cause():
    loan = Loan('L1', date(2026, 10, 12))
    interrupted = InterruptedError('request interrupted')
    failure = PaymentGatewayFailure()
    failure.__cause__ = interrupted
    gateway = PaymentGateway(failure=failure)
    application = FeeApplication(
        LoanRepository([loan]),
        Clock(date(2026, 10, 12)),
        gateway,
    )

    outcome = application.pay('L1')

    assert outcome.succeeded is False
    assert outcome.failure is failure
    assert outcome.failure.__cause__ is interrupted
