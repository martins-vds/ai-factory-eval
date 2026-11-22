import pytest

from src.fees.gateway import HttpPaymentGateway, PaymentGatewayUnavailable
from src.fees.services import PaymentResponse


def test_payment_gateway_sends_post_without_body_and_returns_success(gateway_server):
    base_url, requests = gateway_server(200, b'charged\n')

    response = HttpPaymentGateway(base_url).charge('L1')

    assert response == PaymentResponse(200, 'charged\n')
    assert requests == [('POST', '/charge?loan=L1', b'')]


def test_payment_gateway_maps_non_200_response_to_502(gateway_server):
    base_url, _ = gateway_server(503, b'declined\n')

    response = HttpPaymentGateway(base_url).charge('L2')

    assert response == PaymentResponse(502, 'declined\n')


def test_payment_gateway_preserves_interruption_as_gateway_failure(monkeypatch):
    interruption = InterruptedError('request interrupted')

    def interrupt(*args, **kwargs):
        raise interruption

    monkeypatch.setattr('src.fees.gateway.request.urlopen', interrupt)

    with pytest.raises(PaymentGatewayUnavailable) as failure:
        HttpPaymentGateway('http://127.0.0.1').charge('L1')

    assert failure.value.__cause__ is interruption
