from dataclasses import dataclass
from datetime import date, timedelta

import pytest

from src.fees.services import (
    FeeApplication,
    GatewayResponse,
    PaymentApplication,
    PaymentGatewayError,
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


class Clock:
    def today(self):
        return date(2026, 11, 19)


@pytest.mark.parametrize(
    ('days_late', 'expected_fee_cents'),
    [(2, 0), (3, 75)],
)
def test_fee_is_waived_through_two_days_late_then_charges_the_full_late_days(
    days_late, expected_fee_cents
):
    due_on = date(2026, 1, 16)
    loan = Loan('L1', due_on, returned_on=due_on + timedelta(days=days_late))
    application = FeeApplication(LoanRepository(loan), Clock())

    fee = application.calculate_fee('L1')

    assert (fee.days_late, fee.fee_cents) == (days_late, expected_fee_cents)


def test_fee_is_capped_at_ten_dollars():
    due_on = date(2026, 1, 16)
    loan = Loan('L1', due_on, returned_on=due_on + timedelta(days=50))
    application = FeeApplication(LoanRepository(loan), Clock())

    fee = application.calculate_fee('L1')

    assert (fee.days_late, fee.fee_cents) == (50, 1000)


def test_early_return_has_no_late_days_or_fee():
    due_on = date(2026, 1, 16)
    loan = Loan('L1', due_on, returned_on=due_on - timedelta(days=3))
    application = FeeApplication(LoanRepository(loan), Clock())

    fee = application.calculate_fee('L1')

    assert (fee.days_late, fee.fee_cents) == (0, 0)


def test_unreturned_loan_uses_the_injected_clock():
    loan = Loan('L1', date(2026, 11, 10))
    application = FeeApplication(LoanRepository(loan), Clock())

    fee = application.calculate_fee('L1')

    assert (fee.days_late, fee.fee_cents) == (9, 225)


def test_unknown_loan_has_no_fee_quote():
    application = FeeApplication(LoanRepository(None), Clock())

    assert application.calculate_fee('missing') is None


def test_missing_loan_is_not_charged():
    class PaymentGateway:
        def charge(self, loan_id):
            raise AssertionError('missing loan must not be sent to the gateway')

    application = PaymentApplication(LoanRepository(None), PaymentGateway())

    assert application.pay('missing') is None


def test_successful_gateway_response_remains_successful():
    class PaymentGateway:
        def charge(self, loan_id):
            return GatewayResponse(200, 'charged\n')

    loan = Loan('L1', date(2026, 1, 16))
    application = PaymentApplication(LoanRepository(loan), PaymentGateway())

    result = application.pay('L1')

    assert (result.status_code, result.body) == (200, 'charged\n')


def test_non_success_gateway_response_becomes_bad_gateway():
    class PaymentGateway:
        def charge(self, loan_id):
            return GatewayResponse(503, 'declined\n')

    loan = Loan('L1', date(2026, 1, 16))
    application = PaymentApplication(LoanRepository(loan), PaymentGateway())

    result = application.pay('L1')

    assert (result.status_code, result.body) == (502, 'declined\n')


def test_interrupted_gateway_failure_remains_chained():
    interruption = InterruptedError('request interrupted')
    failure = PaymentGatewayError('payment gateway unavailable')
    failure.__cause__ = interruption

    class PaymentGateway:
        def charge(self, loan_id):
            raise failure

    loan = Loan('L1', date(2026, 1, 16))
    application = PaymentApplication(LoanRepository(loan), PaymentGateway())

    with pytest.raises(PaymentGatewayError) as raised:
        application.pay('L1')

    assert raised.value.__cause__ is interruption
