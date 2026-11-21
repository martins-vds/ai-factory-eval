from io import BytesIO
from urllib.error import HTTPError

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


def test_payment_gateway_uses_the_configured_default(monkeypatch):
    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def read(self):
            return b'charged\n'

    requests = []

    def respond(request):
        requests.append(request.full_url)
        return Response()

    monkeypatch.delenv('PAYMENT_GATEWAY_URL', raising=False)
    monkeypatch.setattr('src.fees.gateway.urlopen', respond)

    response = HttpPaymentGateway().charge('L1')

    assert response.status_code == 200
    assert response.body == 'charged\n'
    assert requests == ['https://payments.lending-library.invalid/charge?loan=L1']


def test_interrupted_error_response_body_preserves_the_interruption(monkeypatch):
    class InterruptedHTTPError(HTTPError):
        def read(self):
            raise InterruptedError('response read interrupted')

    def interrupt(*args, **kwargs):
        raise InterruptedHTTPError('http://gateway.invalid', 503, 'Unavailable', None, BytesIO())

    monkeypatch.setattr('src.fees.gateway.urlopen', interrupt)

    with pytest.raises(PaymentGatewayFailure) as failure:
        HttpPaymentGateway().charge('L1')

    assert isinstance(failure.value.__cause__, InterruptedError)
