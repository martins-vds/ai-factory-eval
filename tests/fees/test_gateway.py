from contextlib import nullcontext
from types import SimpleNamespace

import pytest

from src.fees.gateway import HttpPaymentGateway, PaymentGatewayUnavailable, request
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


def test_payment_gateway_maps_non_error_http_status_to_502(gateway_server):
    base_url, _ = gateway_server(204, b'')

    response = HttpPaymentGateway(base_url).charge('L2')

    assert response == PaymentResponse(502, '')


def test_payment_gateway_uses_the_configured_default_url(monkeypatch):
    monkeypatch.delenv('PAYMENT_GATEWAY_URL', raising=False)
    captured = []
    response = SimpleNamespace(status=200, read=lambda: b'charged\n')

    def open_request(req):
        captured.append(req)
        return nullcontext(response)

    monkeypatch.setattr(request, 'urlopen', open_request)

    result = HttpPaymentGateway().charge('L1')

    assert result == PaymentResponse(200, 'charged\n')
    assert captured[0].full_url == (
        'https://payments.lending-library.invalid/charge?loan=L1'
    )
    assert captured[0].method == 'POST'


def test_payment_gateway_preserves_interruption_as_gateway_failure(monkeypatch):
    interruption = InterruptedError('request interrupted')

    def interrupt(*args, **kwargs):
        raise interruption

    monkeypatch.setattr(request, 'urlopen', interrupt)

    with pytest.raises(PaymentGatewayUnavailable) as failure:
        HttpPaymentGateway('http://127.0.0.1').charge('L1')

    assert failure.value.__cause__ is interruption
