from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

import pytest

from src.fees.services import FeeApplication, GatewayResponse


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


class Clock:
    def __init__(self, today):
        self.value = today

    def today(self):
        return self.value


class PaymentGateway:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.charges = []

    def charge(self, loan_id):
        self.charges.append(loan_id)
        if self.error is not None:
            raise self.error
        return self.response


def application(*loans, today=date(2026, 11, 9), gateway=None):
    return FeeApplication(
        LoanRepository(*loans),
        Clock(today),
        gateway or PaymentGateway(GatewayResponse(200, 'charged\n')),
    )


@pytest.mark.parametrize(
    ('days_late', 'expected'),
    [
        (0, Decimal('0.00')),
        (1, Decimal('0.00')),
        (2, Decimal('0.00')),
        (3, Decimal('0.75')),
        (60, Decimal('10.00')),
    ],
)
def test_fee_for_loan_applies_grace_period_daily_rate_and_cap(days_late, expected):
    due_on = date(2026, 1, 1)
    loan = Loan('L1', due_on)

    fee = application(loan, today=due_on + timedelta(days=days_late)).fee_for('L1')

    assert fee.days_late == days_late
    assert fee.amount == expected


def test_fee_for_loan_uses_return_date_and_never_charges_for_early_returns():
    loan = Loan('L1', date(2026, 1, 10), date(2026, 1, 8))

    fee = application(loan, today=date(2026, 11, 9)).fee_for('L1')

    assert fee.days_late == 0
    assert fee.amount == Decimal('0.00')


def test_fee_for_unknown_loan_returns_none():
    assert application().fee_for('missing') is None


def test_payment_requires_an_existing_loan_before_calling_gateway():
    gateway = PaymentGateway(GatewayResponse(200, 'charged\n'))

    result = application(gateway=gateway).pay('missing')

    assert (result.status, result.body) == (404, 'no such loan\n')
    assert gateway.charges == []


def test_payment_forwards_success_response():
    gateway = PaymentGateway(GatewayResponse(200, 'charged\n'))
    app = application(Loan('L1', date(2026, 11, 1)), gateway=gateway)

    result = app.pay('L1')

    assert (result.status, result.body) == (200, 'charged\n')
    assert result.interruption is None
    assert gateway.charges == ['L1']


def test_payment_maps_non_success_gateway_status_to_bad_gateway():
    gateway = PaymentGateway(GatewayResponse(503, 'declined\n'))
    app = application(Loan('L1', date(2026, 11, 1)), gateway=gateway)

    result = app.pay('L1')

    assert (result.status, result.body) == (502, 'declined\n')


def test_payment_maps_io_failure_to_bad_gateway():
    gateway = PaymentGateway(error=OSError('gateway unavailable'))
    app = application(Loan('L1', date(2026, 11, 1)), gateway=gateway)

    result = app.pay('L1')

    assert (result.status, result.body) == (502, 'payment gateway unavailable\n')


def test_payment_surfaces_interruption_without_losing_it():
    interruption = InterruptedError('gateway call interrupted')
    gateway = PaymentGateway(error=interruption)
    app = application(Loan('L1', date(2026, 11, 1)), gateway=gateway)

    result = app.pay('L1')

    assert (result.status, result.body) == (502, 'payment gateway unavailable\n')
    assert result.interruption is interruption
