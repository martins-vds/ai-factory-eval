import pytest

from src.fees.gateway import GatewayFailure, HttpPaymentGateway


def test_http_payment_gateway_preserves_interruption_when_wrapping_failure(monkeypatch):
    interruption = InterruptedError('payment request interrupted')

    def interrupted(*args, **kwargs):
        raise interruption

    monkeypatch.setattr('src.fees.gateway.request.urlopen', interrupted)

    with pytest.raises(GatewayFailure) as failure:
        HttpPaymentGateway().charge('L1')

    assert failure.value.__cause__ is interruption
