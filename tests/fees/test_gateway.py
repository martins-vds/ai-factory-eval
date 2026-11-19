from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest

from src.fees import gateway
from src.fees.services import PaymentGatewayError
from src.fees.gateway import HttpPaymentGateway


@pytest.fixture
def local_gateway():
    class Handler(BaseHTTPRequestHandler):
        requests = []

        def do_POST(self):
            body = self.rfile.read(int(self.headers.get('Content-Length', '0')))
            self.requests.append((self.command, self.path, body))
            if self.path.endswith('loan=L1'):
                self.send_response(200)
                response_body = b'charged\n'
            else:
                self.send_response(503)
                response_body = b'declined\n'
            self.end_headers()
            self.wfile.write(response_body)

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}', Handler.requests
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


def test_payment_gateway_sends_post_without_body_and_returns_gateway_response(local_gateway):
    base_url, requests = local_gateway
    gateway = HttpPaymentGateway(base_url)

    response = gateway.charge('L1')

    assert (response.status_code, response.body) == (200, 'charged\n')
    assert requests == [('POST', '/charge?loan=L1', b'')]


def test_payment_gateway_returns_non_success_body_for_application_mapping(local_gateway):
    base_url, requests = local_gateway
    gateway = HttpPaymentGateway(base_url)

    response = gateway.charge('L2')

    assert (response.status_code, response.body) == (503, 'declined\n')
    assert requests == [('POST', '/charge?loan=L2', b'')]


def test_payment_gateway_keeps_interrupted_failure_as_exception_cause(monkeypatch):
    interruption = InterruptedError('request interrupted')

    def interrupt_request(*args, **kwargs):
        raise interruption

    monkeypatch.setattr(gateway, 'urlopen', interrupt_request)

    with pytest.raises(PaymentGatewayError) as raised:
        HttpPaymentGateway('http://payments.example').charge('L1')

    assert raised.value.__cause__ is interruption
