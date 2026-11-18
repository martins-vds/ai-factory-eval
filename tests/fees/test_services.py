from datetime import date, timedelta

import pytest

from src.fees.services import (
    FeeApplication,
    FeeQuote,
    GatewayResponse,
    GatewayUnavailable,
    PaymentApplication,
    PaymentFailed,
    calculate_late_fee,
)


def test_fee_is_twenty_five_cents_per_day_after_grace_period():
    due_on = date(2026, 5, 1)

    fee = calculate_late_fee(due_on, None, due_on + timedelta(days=3))

    assert fee == FeeQuote(late_days=3, amount_cents=75)


def test_fee_waives_up_to_two_days_and_caps_at_ten_dollars():
    due_on = date(2026, 5, 1)

    assert calculate_late_fee(due_on, None, due_on + timedelta(days=2)) == FeeQuote(2, 0)
    assert calculate_late_fee(due_on, None, due_on + timedelta(days=41)) == FeeQuote(41, 1000)


def test_fee_uses_return_date_and_never_counts_early_days_as_late():
    due_on = date(2026, 5, 1)

    fee = calculate_late_fee(
        due_on,
        due_on + timedelta(days=3),
        due_on + timedelta(days=20),
    )
    early_fee = calculate_late_fee(
        due_on,
        due_on - timedelta(days=1),
        due_on + timedelta(days=20),
    )

    assert fee == FeeQuote(3, 75)
    assert early_fee == FeeQuote(0, 0)


def test_fee_use_case_returns_no_quote_for_an_unknown_loan():
    class Repository:
        def find(self, loan_id):
            return None

    class Clock:
        def today(self):
            raise AssertionError('the clock should not be read for an unknown loan')

    assert FeeApplication(Repository(), Clock()).quote('missing') is None


def test_payment_use_case_does_not_call_gateway_for_an_unknown_loan():
    class Repository:
        def find(self, loan_id):
            return None

    class Gateway:
        calls = 0

        def charge(self, loan_id):
            self.calls += 1

    gateway = Gateway()

    result = PaymentApplication(Repository(), gateway).pay('missing')

    assert result is None
    assert gateway.calls == 0


def test_payment_use_case_maps_non_success_gateway_response_to_failure():
    class Repository:
        def find(self, loan_id):
            return object()

    class Gateway:
        def charge(self, loan_id):
            return GatewayResponse(503, b'declined\n')

    with pytest.raises(PaymentFailed) as failure:
        PaymentApplication(Repository(), Gateway()).pay('L3')

    assert failure.value.body == b'declined\n'


def test_payment_use_case_preserves_gateway_interruption_as_a_failure():
    class Repository:
        def find(self, loan_id):
            return object()

    class Gateway:
        def charge(self, loan_id):
            try:
                raise InterruptedError('request interrupted')
            except InterruptedError as error:
                raise GatewayUnavailable from error

    with pytest.raises(PaymentFailed) as failure:
        PaymentApplication(Repository(), Gateway()).pay('L3')

    assert isinstance(failure.value.__cause__, InterruptedError)
