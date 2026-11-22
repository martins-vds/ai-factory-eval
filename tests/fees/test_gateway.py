from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest

from src.fees.gateway import HttpPaymentGateway


@pytest.fixture
def payment_gateway_server():
    requests = []
    response = {'status': 200, 'body': b'charged\n'}

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
            requests.append((self.command, self.path, body))
            self.send_response(response['status'])
            self.send_header(
                'Content-Length',
                str(response.get('content_length', len(response['body']))),
            )
            self.end_headers()
            self.wfile.write(response['body'])

        def log_message(self, format, *args):
            return

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}', response, requests
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


@pytest.mark.parametrize(
    ('gateway_status', 'gateway_body', 'expected_status'),
    [(200, b'charged\n', 200), (503, b'declined\n', 503)],
)
def test_gateway_posts_empty_body_and_returns_gateway_response(
    payment_gateway_server, gateway_status, gateway_body, expected_status
):
    base_url, response, requests = payment_gateway_server
    response.update(status=gateway_status, body=gateway_body)

    result = HttpPaymentGateway(f'{base_url}/prefixX/').charge('L/1')

    assert (result.status, result.body) == (expected_status, gateway_body)
    assert requests == [('POST', '/prefixX/charge?loan=L%2F1', b'')]


def test_gateway_reads_configured_url(monkeypatch):
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', 'https://payments.example.test/custom')

    assert HttpPaymentGateway().base_url == 'https://payments.example.test/custom'


def test_gateway_translates_incomplete_response_to_io_error(payment_gateway_server):
    base_url, response, _ = payment_gateway_server
    response.update(status=200, body=b'partial\n', content_length=20)

    with pytest.raises(OSError):
        HttpPaymentGateway(base_url).charge('L1')


def test_gateway_uses_characterized_default_url(monkeypatch):
    monkeypatch.delenv('PAYMENT_GATEWAY_URL', raising=False)

    assert HttpPaymentGateway().base_url == 'https://payments.lending-library.invalid'


def test_gateway_uses_bounded_request_timeout(payment_gateway_server, monkeypatch):
    base_url, response, _ = payment_gateway_server
    response.update(status=200, body=b'charged\n')
    timeouts = []

    def open_url(request, timeout):
        timeouts.append(timeout)
        return real_urlopen(request, timeout=timeout)

    from src.fees.gateway import urlopen as real_urlopen

    monkeypatch.setattr('src.fees.gateway.urlopen', open_url)

    HttpPaymentGateway(base_url).charge('L1')

    assert timeouts == [5]
