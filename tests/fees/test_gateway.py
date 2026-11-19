from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest

from src.fees import gateway
from src.fees.gateway import HttpPaymentGateway
from src.fees.services import PaymentGatewayError


@pytest.fixture
def gateway_server():
    requests = []

    class Handler(BaseHTTPRequestHandler):
        response_status = 200
        response_body = b'charged\n'

        def do_POST(self):
            body = self.rfile.read(int(self.headers.get('Content-Length', '0')))
            requests.append((self.command, self.path, body))
            self.send_response(self.response_status)
            self.end_headers()
            self.wfile.write(self.response_body)

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = Thread(target=server.serve_forever)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}', Handler, requests
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


def test_gateway_posts_an_empty_charge_request(gateway_server):
    base_url, _, requests = gateway_server

    response = HttpPaymentGateway(base_url).charge('L1')

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
