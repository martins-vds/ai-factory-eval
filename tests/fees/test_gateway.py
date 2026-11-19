import pytest

from src.fees import gateway
from src.fees.gateway import HttpPaymentGateway
from src.fees.services import PaymentGatewayError


def test_gateway_posts_an_empty_charge_request(gateway_server, monkeypatch):
    base_url, _, requests = gateway_server
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', base_url)

    response = HttpPaymentGateway().charge('L1')

    assert (response.status_code, response.body) == (200, 'charged\n')
    assert requests == [('POST', '/charge?loan=L1', b'')]


def test_interrupted_request_is_wrapped_without_losing_the_interruption(monkeypatch):
    interruption = InterruptedError('request interrupted')

    def interrupt(request):
        raise interruption

    monkeypatch.setattr(gateway, 'urlopen', interrupt)

    with pytest.raises(PaymentGatewayError) as raised:
        HttpPaymentGateway('http://payments.invalid').charge('L1')

    assert raised.value.__cause__ is interruption
