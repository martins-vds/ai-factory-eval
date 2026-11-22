import pytest

from src.fees.gateway import HttpPaymentGateway
from src.fees.services import GatewayResponse, PaymentGatewayInterrupted, PaymentGatewayUnavailable


def test_gateway_posts_empty_body_to_charge_endpoint(payment_gateway_server):
    requests, _ = payment_gateway_server

    response = HttpPaymentGateway().charge('L1')

    assert response == GatewayResponse(200, 'charged\n')
    assert requests == [('POST', '/charge?loan=L1', b'')]


def test_gateway_returns_non_success_response_for_application_mapping(payment_gateway_server):
    requests, reply = payment_gateway_server
    reply.update(status=503, body=b'declined\n')

    response = HttpPaymentGateway().charge('L2')

    assert response == GatewayResponse(503, 'declined\n')
    assert requests == [('POST', '/charge?loan=L2', b'')]


def test_gateway_wraps_connection_failure():
    import socket

    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        port = listener.getsockname()[1]

    with pytest.raises(PaymentGatewayUnavailable):
        HttpPaymentGateway(f'http://127.0.0.1:{port}').charge('L1')


def test_gateway_preserves_interrupted_request(monkeypatch):
    import urllib.request

    interruption = InterruptedError('request interrupted')

    def interrupt_request(*args, **kwargs):
        raise interruption

    monkeypatch.setattr(urllib.request, 'urlopen', interrupt_request)

    with pytest.raises(PaymentGatewayInterrupted) as raised:
        HttpPaymentGateway('http://127.0.0.1:8080').charge('L1')

    assert raised.value.__cause__ is interruption


def test_gateway_preserves_interruption_wrapped_by_urllib(monkeypatch):
    import urllib.error
    import urllib.request

    interruption = InterruptedError('request interrupted')

    def interrupt_request(*args, **kwargs):
        raise urllib.error.URLError(interruption)

    monkeypatch.setattr(urllib.request, 'urlopen', interrupt_request)

    with pytest.raises(PaymentGatewayInterrupted) as raised:
        HttpPaymentGateway('http://127.0.0.1:8080').charge('L1')

    assert raised.value.__cause__ is interruption
