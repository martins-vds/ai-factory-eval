import pytest

from src.fees.gateway import HttpPaymentGateway
from src.fees.services import GatewayUnavailable


def test_interrupted_gateway_call_surfaces_as_failure_without_losing_interrupt(
    monkeypatch,
):
    def interrupt(request):
        raise InterruptedError('request interrupted')

    class Opener:
        def open(self, request):
            return interrupt(request)

    monkeypatch.setattr('src.fees.gateway.build_opener', lambda *handlers: Opener())
    with pytest.raises(GatewayUnavailable) as failure:
        HttpPaymentGateway('http://127.0.0.1:1').charge('L3')

    assert failure.value.body == b'payment gateway unavailable\n'
    assert isinstance(failure.value.__cause__, InterruptedError)
