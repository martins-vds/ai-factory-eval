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


def test_gateway_uses_explicit_base_url_instead_of_environment(payment_gateway_server, monkeypatch):
    requests, reply = payment_gateway_server
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', 'http://127.0.0.1:1')

    response = HttpPaymentGateway(reply['base_url']).charge('L3')

    assert response == GatewayResponse(200, 'charged\n')
    assert requests == [('POST', '/charge?loan=L3', b'')]


def test_gateway_does_not_follow_redirects(payment_gateway_server):
    requests, reply = payment_gateway_server
    reply.update(status=302, body=b'redirected\n', location='/redirected')

    response = HttpPaymentGateway().charge('L4')

    assert response == GatewayResponse(302, 'redirected\n')
    assert requests == [('POST', '/charge?loan=L4', b'')]


@pytest.mark.parametrize(
    ('status', 'body'),
    [
        (200, b'\xff'),
        (503, b'\xff'),
    ],
)
def test_gateway_decodes_invalid_utf8_like_java_gateway(payment_gateway_server, status, body):
    requests, reply = payment_gateway_server
    reply.update(status=status, body=body)

    response = HttpPaymentGateway().charge('L5')

    assert response == GatewayResponse(status, '\ufffd')
    assert requests == [('POST', '/charge?loan=L5', b'')]


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

    class Opener:
        def open(self, request):
            raise interruption

    monkeypatch.setattr(urllib.request, 'build_opener', lambda *args: Opener())

    with pytest.raises(PaymentGatewayInterrupted) as raised:
        HttpPaymentGateway('http://127.0.0.1:8080').charge('L1')

    assert raised.value.__cause__ is interruption


def test_gateway_preserves_interruption_wrapped_by_urllib(monkeypatch):
    import urllib.error
    import urllib.request

    interruption = InterruptedError('request interrupted')

    class Opener:
        def open(self, request):
            raise urllib.error.URLError(interruption)

    monkeypatch.setattr(urllib.request, 'build_opener', lambda *args: Opener())

    with pytest.raises(PaymentGatewayInterrupted) as raised:
        HttpPaymentGateway('http://127.0.0.1:8080').charge('L1')

    assert raised.value.__cause__ is interruption


def test_gateway_uses_the_configured_default_url(monkeypatch):
    import urllib.request

    monkeypatch.delenv('PAYMENT_GATEWAY_URL', raising=False)
    requests = []

    class Opener:
        def open(self, request):
            requests.append(request.full_url)
            raise InterruptedError('request interrupted')

    monkeypatch.setattr(urllib.request, 'build_opener', lambda *args: Opener())

    with pytest.raises(PaymentGatewayInterrupted):
        HttpPaymentGateway().charge('L6')

    assert requests == ['https://payments.lending-library.invalid/charge?loan=L6']


def test_gateway_maps_error_response_body_read_failure_to_unavailable(monkeypatch):
    import urllib.error
    import urllib.request

    read_error = OSError('response body read failed')

    class FailedBody:
        closed = False

        def read(self, *args):
            raise read_error

        def close(self):
            self.closed = True

    response = urllib.error.HTTPError(
        'http://127.0.0.1/charge?loan=L7',
        503,
        'Service Unavailable',
        {},
        FailedBody(),
    )

    class Opener:
        def open(self, request):
            raise response

    monkeypatch.setattr(urllib.request, 'build_opener', lambda *args: Opener())

    with pytest.raises(PaymentGatewayUnavailable) as raised:
        HttpPaymentGateway('http://127.0.0.1').charge('L7')

    assert raised.value.__cause__ is read_error
