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
        HttpPaymentGateway().charge('L3')

    assert failure.value.body == b'payment gateway unavailable\n'
    assert isinstance(failure.value.__cause__, InterruptedError)


def test_gateway_uses_the_characterized_default_url_when_unconfigured(monkeypatch):
    urls = []

    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b'charged\n'

    class Opener:
        def open(self, request):
            urls.append(request.full_url)
            return Response()

    monkeypatch.delenv('PAYMENT_GATEWAY_URL', raising=False)
    monkeypatch.setattr('src.fees.gateway.build_opener', lambda *handlers: Opener())

    result = HttpPaymentGateway().charge('L3')

    assert result.body == b'charged\n'
    assert urls == ['https://payments.lending-library.invalid/charge?loan=L3']
