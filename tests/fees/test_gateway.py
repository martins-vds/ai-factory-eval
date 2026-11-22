from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from unittest.mock import patch

import pytest

from src.fees.services import FeeApplication, GatewayUnavailable
from src.fees.gateway import HttpPaymentGateway


class PaymentServer(ThreadingHTTPServer):
    def __init__(self):
        super().__init__(('127.0.0.1', 0), PaymentHandler)
        self.requests = []
        self.response_status = 200
        self.response_body = b'charged\n'


class PaymentHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.server.requests.append(
            (self.command, self.path, self.rfile.read(int(self.headers.get('Content-Length', 0))))
        )
        self.send_response(self.server.response_status)
        self.end_headers()
        self.wfile.write(self.server.response_body)

    def log_message(self, format, *args):
        pass


@pytest.fixture
def payment_server():
    server = PaymentServer()
    thread = Thread(target=server.serve_forever)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


def test_gateway_posts_empty_body_and_preserves_gateway_response(payment_server):
    gateway = HttpPaymentGateway(f'http://127.0.0.1:{payment_server.server_port}')

    response = gateway.charge('L1')

    assert payment_server.requests == [('POST', '/charge?loan=L1', b'')]
    assert (response.status_code, response.body) == (200, 'charged\n')


def test_payment_maps_non_200_gateway_response_to_502_and_preserves_body(payment_server):
    payment_server.response_status = 503
    payment_server.response_body = b'declined\n'
    gateway = HttpPaymentGateway(f'http://127.0.0.1:{payment_server.server_port}')
    application = FeeApplication(
        repository=type('Loans', (), {'find': lambda self, loan_id: object()})(),
        clock=None,
        gateway=gateway,
    )

    response = application.pay('L1')

    assert (response.status_code, response.body) == (502, 'declined\n')


def test_interrupted_gateway_call_is_reported_without_losing_interruption():
    gateway = HttpPaymentGateway('http://127.0.0.1:1')

    with patch('src.fees.gateway.urlopen', side_effect=InterruptedError('interrupted')):
        with pytest.raises(GatewayUnavailable) as failure:
            gateway.charge('L1')

    assert isinstance(failure.value.__cause__, InterruptedError)
