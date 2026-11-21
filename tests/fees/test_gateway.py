import pytest

from src.fees.gateway import HttpPaymentGateway
from src.fees.services import PaymentGatewayFailure


def test_payment_gateway_preserves_interrupted_error(monkeypatch):
    def interrupt(*args, **kwargs):
        raise InterruptedError('request interrupted')

    monkeypatch.setattr('src.fees.gateway.urlopen', interrupt)

    with pytest.raises(PaymentGatewayFailure) as failure:
        HttpPaymentGateway().charge('L1')

    assert isinstance(failure.value.__cause__, InterruptedError)
