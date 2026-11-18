from dataclasses import FrozenInstanceError, dataclass
from datetime import date, timedelta
from io import BytesIO
from urllib.error import HTTPError

import pytest

from src.fees.gateway import HttpPaymentGateway
from src.fees.services import (
    FeeApplication,
    GatewayResponse,
    PaymentApplication,
    PaymentGatewayError,
    PaymentResult,
)


@dataclass
class LoanRecord:
    id: str
    due_on: date
    returned_on: date | None = None


class FakeLoanRepository:
    def __init__(self, loan):
        self.loan = loan

    def find(self, loan_id):
        return self.loan if self.loan and self.loan.id == loan_id else None

    def all(self):
        return [self.loan] if self.loan else []


class FixedClock:
    def __init__(self, today):
        self.value = today

    def today(self):
        return self.value


class FakeResponse:
    def __init__(self, status, body):
        self.status = status
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return self.body


class RecordingOpener:
    def __init__(self, status=200, body=b'charged\n'):
        self.response = FakeResponse(status, body)
        self.requests = []

    def open(self, request):
        self.requests.append(request)
        return self.response


@pytest.mark.parametrize(
    ('late_days', 'amount_cents'),
    [(0, 0), (2, 0), (3, 75), (40, 1000), (41, 1000)],
)
def test_fee_calculation_applies_grace_period_and_cap(late_days, amount_cents):
    due_on = date(2026, 1, 1)
    loan = LoanRecord('L1', due_on)
    fees = FeeApplication(
        FakeLoanRepository(loan),
        FixedClock(due_on + timedelta(days=late_days)),
    )

    fee = fees.calculate('L1')

    assert fee.late_days == late_days
    assert fee.amount_cents == amount_cents


def test_fee_quote_formats_money_and_is_immutable():
    due_on = date(2026, 1, 1)
    fees = FeeApplication(
        FakeLoanRepository(LoanRecord('L1', due_on)),
        FixedClock(due_on + timedelta(days=3)),
    )

    fee = fees.calculate('L1')

    assert fee.amount == '$0.75'
    with pytest.raises(FrozenInstanceError):
        fee.amount_cents = 100
    capped_fee = FeeApplication(
        FakeLoanRepository(LoanRecord('L2', due_on)),
        FixedClock(due_on + timedelta(days=41)),
    ).calculate('L2')
    assert capped_fee.amount == '$10.00'


def test_fee_calculation_uses_return_date_instead_of_today():
    due_on = date(2026, 1, 1)
    loan = LoanRecord('L1', due_on, returned_on=due_on + timedelta(days=3))
    fees = FeeApplication(FakeLoanRepository(loan), FixedClock(due_on + timedelta(days=30)))

    fee = fees.calculate('L1')

    assert fee.late_days == 3
    assert fee.amount_cents == 75


def test_fee_calculation_clamps_days_before_due_date():
    due_on = date(2026, 1, 1)
    fees = FeeApplication(
        FakeLoanRepository(LoanRecord('L1', due_on)),
        FixedClock(due_on - timedelta(days=3)),
    )

    fee = fees.calculate('L1')

    assert fee.late_days == 0
    assert fee.amount_cents == 0


def test_fee_calculation_returns_none_for_unknown_loan():
    fees = FeeApplication(FakeLoanRepository(None), FixedClock(date(2026, 1, 1)))

    assert fees.calculate('missing') is None


def test_gateway_failure_retains_interruption():
    class InterruptingOpener:
        def open(self, request):
            raise InterruptedError('payment request interrupted')

    gateway = HttpPaymentGateway(base_url='http://payments.invalid', opener=InterruptingOpener())

    with pytest.raises(PaymentGatewayError) as failure:
        gateway.charge('L1')

    assert str(failure.value) == 'payment gateway unavailable'
    assert isinstance(failure.value.__cause__, InterruptedError)


def test_gateway_uses_configured_url_and_encodes_loan_id():
    opener = RecordingOpener()
    gateway = HttpPaymentGateway(base_url='https://payments.exampleX/', opener=opener)

    response = gateway.charge('L1&next=other')

    assert response == GatewayResponse(200, 'charged\n')
    assert opener.requests[0].full_url == (
        'https://payments.exampleX/charge?loan=L1%26next%3Dother'
    )
    assert opener.requests[0].get_method() == 'POST'
    assert opener.requests[0].data is None


def test_gateway_uses_characterized_default_url(monkeypatch):
    monkeypatch.delenv('PAYMENT_GATEWAY_URL', raising=False)
    opener = RecordingOpener()
    gateway = HttpPaymentGateway(opener=opener)

    gateway.charge('L1')

    assert opener.requests[0].full_url == (
        'https://payments.lending-library.invalid/charge?loan=L1'
    )


def test_gateway_replaces_invalid_utf8_in_success_body():
    gateway = HttpPaymentGateway(
        base_url='https://payments.example',
        opener=RecordingOpener(body=b'\xff'),
    )

    response = gateway.charge('L1')

    assert response.body == '\ufffd'


def test_gateway_replaces_invalid_utf8_in_http_error_body():
    class ErrorOpener:
        def open(self, request):
            raise HTTPError(request.full_url, 503, 'unavailable', {}, BytesIO(b'\xff'))

    gateway = HttpPaymentGateway(
        base_url='https://payments.example',
        opener=ErrorOpener(),
    )

    response = gateway.charge('L1')

    assert response.status_code == 503
    assert response.body == '\ufffd'


def test_payment_application_maps_and_retains_interrupted_gateway_failure():
    class InterruptedGateway:
        def charge(self, loan_id):
            try:
                raise InterruptedError('payment request interrupted')
            except InterruptedError as exc:
                raise PaymentGatewayError('payment gateway unavailable') from exc

    payments = PaymentApplication(
        FakeLoanRepository(LoanRecord('L1', date(2026, 1, 1))),
        InterruptedGateway(),
    )

    result = payments.pay('L1')

    assert result.status_code == 502
    assert result.body == 'payment gateway unavailable\n'
    assert isinstance(result.failure.__cause__, InterruptedError)


def test_payment_result_defaults_and_immutability():
    loan = LoanRecord('L1', date(2026, 1, 1))
    result = PaymentResult(200, 'charged\n', loan=loan)
    gateway_response = GatewayResponse(200, 'charged\n')

    assert result.succeeded is True
    assert result.failure is None
    assert result.loan is loan
    with pytest.raises(FrozenInstanceError):
        result.status_code = 502
    with pytest.raises(FrozenInstanceError):
        gateway_response.status_code = 502


def test_unknown_payment_result_is_not_found_without_gateway_call():
    class UnusedGateway:
        def charge(self, loan_id):
            pytest.fail('unknown loans must not reach the gateway')

    result = PaymentApplication(
        FakeLoanRepository(None),
        UnusedGateway(),
    ).pay('missing')

    assert result.status_code == 404
    assert result.body == 'no such loan\n'
    assert result.failure is None
    assert result.loan is None


@pytest.mark.parametrize(
    ('gateway_status', 'expected_status'),
    [(200, 200), (503, 502)],
)
def test_payment_application_maps_gateway_status_and_preserves_body(
    gateway_status, expected_status
):
    loan = LoanRecord('L1', date(2026, 1, 1))

    class RespondingGateway:
        def charge(self, loan_id):
            return GatewayResponse(gateway_status, 'gateway response\n')

    result = PaymentApplication(
        FakeLoanRepository(loan),
        RespondingGateway(),
    ).pay('L1')

    assert result.status_code == expected_status
    assert result.body == 'gateway response\n'
    assert result.failure is None
    assert result.loan is loan
