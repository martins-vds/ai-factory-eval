import urllib.request

import pytest

from src.fees.gateway import HttpPaymentGateway, PaymentGatewayInterrupted


def test_interrupted_gateway_call_preserves_the_interruption(monkeypatch):
    interruption = InterruptedError('gateway call interrupted')

    def interrupt(*args, **kwargs):
        raise interruption

    monkeypatch.setattr(urllib.request, 'urlopen', interrupt)
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', 'http://127.0.0.1:8000')

    with pytest.raises(PaymentGatewayInterrupted) as failure:
        HttpPaymentGateway().charge('L1')

    assert failure.value.__cause__ is interruption
