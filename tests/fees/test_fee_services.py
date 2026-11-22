from dataclasses import dataclass
from datetime import date, timedelta

import pytest

from src.fees.services import FeeApplication, GatewayResponse, PaymentApplication


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
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.loan_ids = []

    def charge(self, loan_id):
        self.loan_ids.append(loan_id)
        if self.error is not None:
            raise self.error
        return self.response


@pytest.mark.parametrize(
    ('late_days', 'expected_cents'),
    [(0, 0), (2, 0), (3, 75), (40, 1000), (165, 1000)],
)
def test_fee_for_loan_applies_grace_period_daily_rate_and_cap(late_days, expected_cents):
    due_on = date(2026, 1, 16)
    loan = Loan('L1', due_on)
    application = FeeApplication(
        LoanRepository(loan),
        FixedClock(due_on + timedelta(days=late_days)),
    )

    fee = application.calculate('L1')

    assert fee.days_late == late_days
    assert fee.amount_cents == expected_cents


def test_fee_for_returned_loan_uses_return_date_and_never_counts_early_days():
    due_on = date(2026, 1, 16)
    loan = Loan('L3', due_on, returned_on=date(2026, 2, 4))
    application = FeeApplication(LoanRepository(loan), FixedClock(date(2026, 11, 22)))

    fee = application.calculate('L3')

    assert fee.days_late == 19
    assert fee.amount_cents == 475


def test_early_return_has_no_late_days_or_fee():
    due_on = date(2026, 1, 16)
    loan = Loan('L2', due_on, returned_on=date(2026, 1, 10))
    application = FeeApplication(LoanRepository(loan), FixedClock(date(2026, 11, 22)))

    fee = application.calculate('L2')

    assert fee.days_late == 0
    assert fee.amount_cents == 0


def test_fee_for_unknown_loan_is_absent():
    application = FeeApplication(LoanRepository(), FixedClock(date(2026, 11, 22)))

    assert application.calculate('L9') is None


def test_payment_for_unknown_loan_does_not_call_gateway():
    gateway = PaymentGateway(GatewayResponse(200, b'charged\n'))
    application = PaymentApplication(LoanRepository(), gateway)

    result = application.pay('L9')

    assert (result.status, result.body) == (404, b'no such loan\n')
    assert gateway.loan_ids == []


@pytest.mark.parametrize(
    ('gateway_response', 'expected_status', 'expected_body'),
    [
        (GatewayResponse(200, b'charged\n'), 200, b'charged\n'),
        (GatewayResponse(503, b'declined\n'), 502, b'declined\n'),
    ],
)
def test_payment_maps_gateway_response(gateway_response, expected_status, expected_body):
    gateway = PaymentGateway(gateway_response)
    application = PaymentApplication(LoanRepository(Loan('L1', date(2026, 1, 16))), gateway)

    result = application.pay('L1')

    assert (result.status, result.body) == (expected_status, expected_body)
    assert gateway.loan_ids == ['L1']


def test_payment_failure_keeps_interruption_context():
    interruption = InterruptedError('gateway request interrupted')
    gateway = PaymentGateway(error=interruption)
    application = PaymentApplication(LoanRepository(Loan('L1', date(2026, 1, 16))), gateway)

    result = application.pay('L1')

    assert (result.status, result.body) == (502, b'payment gateway unavailable\n')
    assert result.interruption is interruption


def test_payment_io_failure_maps_to_gateway_unavailable():
    gateway = PaymentGateway(error=OSError('connection refused'))
    application = PaymentApplication(LoanRepository(Loan('L1', date(2026, 1, 16))), gateway)

    result = application.pay('L1')

    assert (result.status, result.body) == (502, b'payment gateway unavailable\n')
