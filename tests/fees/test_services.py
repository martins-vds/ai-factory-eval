from dataclasses import dataclass
from datetime import date
from decimal import Decimal

import pytest

from src.fees.services import FeeApplication, GatewayResponse, PaymentGatewayFailure


@dataclass
class FeeLoan:
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


class RecordingGateway:
    def __init__(self, response=None, failure=None):
        self.response = response
        self.failure = failure
        self.calls = []

    def charge(self, loan_id):
        self.calls.append(loan_id)
        if self.failure is not None:
            raise self.failure
        return self.response


@pytest.mark.parametrize(
    ('due_on', 'returned_on', 'today', 'late_days', 'amount'),
    [
        (date(2026, 1, 2), None, date(2026, 1, 1), 0, Decimal('0.00')),
        (date(2026, 1, 1), None, date(2026, 1, 3), 2, Decimal('0.00')),
        (date(2026, 1, 1), None, date(2026, 1, 4), 3, Decimal('0.75')),
        (date(2026, 1, 1), None, date(2026, 5, 1), 120, Decimal('10.00')),
        (date(2026, 1, 1), date(2026, 1, 2), date(2026, 5, 1), 1, Decimal('0.00')),
    ],
)
def test_fee_calculation_matches_characterized_days_grace_rate_and_cap(
    due_on, returned_on, today, late_days, amount
):
    application = FeeApplication(
        LoanRepository(FeeLoan('L1', due_on, returned_on)),
        FixedClock(today),
        RecordingGateway(),
    )

    quote = application.fee_for('L1')

    assert quote.late_days == late_days
    assert quote.amount == amount


def test_fee_for_unknown_loan_returns_no_quote():
    application = FeeApplication(LoanRepository(), FixedClock(date(2026, 1, 1)), RecordingGateway())

    assert application.fee_for('missing') is None


def test_payment_does_not_call_gateway_when_loan_is_missing():
    gateway = RecordingGateway()
    application = FeeApplication(LoanRepository(), FixedClock(date(2026, 1, 1)), gateway)

    result = application.pay('missing')

    assert result is None
    assert gateway.calls == []


@pytest.mark.parametrize(
    ('gateway_status', 'expected_status'),
    [(200, 200), (503, 502)],
)
def test_payment_maps_only_gateway_success_to_success(gateway_status, expected_status):
    gateway = RecordingGateway(GatewayResponse(gateway_status, 'gateway body\n'))
    application = FeeApplication(
        LoanRepository(FeeLoan('L1', date(2026, 1, 1))),
        FixedClock(date(2026, 1, 1)),
        gateway,
    )

    result = application.pay('L1')

    assert result.status_code == expected_status
    assert result.body == 'gateway body\n'
    assert result.failure is None
    assert gateway.calls == ['L1']


@pytest.mark.parametrize('error_type', [InterruptedError, ConnectionError])
def test_payment_failure_preserves_io_error_cause(error_type):
    def failed_gateway_call():
        try:
            raise error_type('gateway request failed')
        except error_type as error:
            raise PaymentGatewayFailure('payment gateway unavailable') from error

    with pytest.raises(PaymentGatewayFailure) as failure:
        failed_gateway_call()

    application = FeeApplication(
        LoanRepository(FeeLoan('L1', date(2026, 1, 1))),
        FixedClock(date(2026, 1, 1)),
        RecordingGateway(failure=failure.value),
    )

    result = application.pay('L1')

    assert result.status_code == 502
    assert result.body == 'payment gateway unavailable\n'
    assert result.failure is failure.value
    assert isinstance(result.failure.__cause__, error_type)
