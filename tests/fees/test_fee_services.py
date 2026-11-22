from dataclasses import dataclass
from datetime import date

import pytest

from src.fees.gateway import HttpPaymentGateway
from src.fees.services import (
    FeeApplication,
    GatewayResponse,
    GatewayUnavailable,
    LoanNotFound,
    PaymentApplication,
)


@dataclass
class FeeLoan:
    id: str
    due_on: date
    returned_on: date | None = None


class LoanRepository:
    def __init__(self, loan):
        self.loan = loan

    def find(self, loan_id):
        return self.loan if self.loan and self.loan.id == loan_id else None


class FixedClock:
    def today(self):
        return date(2026, 11, 22)


class PaymentGateway:
    def __init__(self, response=None):
        self.response = response
        self.calls = []

    def charge(self, loan_id):
        self.calls.append(loan_id)
        return self.response


@pytest.mark.parametrize(
    ('due_on', 'returned_on', 'expected_days', 'expected_cents'),
    [
        (date(2026, 11, 23), None, 0, 0),
        (date(2026, 11, 20), None, 2, 0),
        (date(2026, 11, 19), None, 3, 75),
        (date(2026, 10, 1), None, 52, 1000),
        (date(2025, 12, 15), date(2026, 1, 3), 19, 475),
    ],
)
def test_fee_application_calculates_late_days_and_capped_cents(
    due_on, returned_on, expected_days, expected_cents
):
    loan = FeeLoan('L1', due_on, returned_on)
    application = FeeApplication(LoanRepository(loan), FixedClock())

    quote = application.calculate('L1')

    assert (quote.days_late, quote.fee_cents) == (expected_days, expected_cents)


def test_fee_application_returns_none_for_an_unknown_loan():
    application = FeeApplication(LoanRepository(None), FixedClock())

    assert application.calculate('missing') is None


def test_payment_application_requires_a_loan_before_calling_gateway():
    gateway = PaymentGateway(GatewayResponse(200, b'charged\n'))
    application = PaymentApplication(LoanRepository(None), gateway)

    with pytest.raises(LoanNotFound):
        application.pay('missing')

    assert gateway.calls == []


@pytest.mark.parametrize(
    ('gateway_status', 'expected_status'),
    [(200, 200), (503, 502)],
)
def test_payment_application_maps_gateway_status(gateway_status, expected_status):
    loan = FeeLoan('L1', date(2026, 11, 22))
    gateway = PaymentGateway(GatewayResponse(gateway_status, b'gateway response\n'))
    application = PaymentApplication(LoanRepository(loan), gateway)

    result = application.pay('L1')

    assert (result.status, result.body) == (expected_status, b'gateway response\n')


def test_payment_application_preserves_interruption_as_gateway_failure_cause(monkeypatch):
    interruption = InterruptedError('gateway call interrupted')

    def interrupt_request(_request):
        raise interruption

    monkeypatch.setattr('src.fees.gateway.urlopen', interrupt_request)
    application = PaymentApplication(
        LoanRepository(FeeLoan('L1', date(2026, 11, 22))),
        HttpPaymentGateway(),
    )

    with pytest.raises(GatewayUnavailable) as failure:
        application.pay('L1')

    assert str(failure.value) == 'payment gateway unavailable'
    assert failure.value.__cause__ is interruption


def test_http_gateway_uses_the_configured_default(monkeypatch):
    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            pass

        def read(self):
            return b'charged\n'

    requests = []

    def open_request(request):
        requests.append(request)
        return Response()

    monkeypatch.delenv('PAYMENT_GATEWAY_URL', raising=False)
    monkeypatch.setattr('src.fees.gateway.urlopen', open_request)

    response = HttpPaymentGateway().charge('L1')

    assert response.body == b'charged\n'
    assert requests[0].get_method() == 'POST'
    assert requests[0].full_url == ('https://payments.lending-library.invalid/charge?loan=L1')
