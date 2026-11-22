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
            self.send_header('Content-Length', str(len(response['body'])))
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

    result = HttpPaymentGateway(base_url).charge('L1')

    assert (result.status, result.body) == (expected_status, gateway_body)
    assert requests == [('POST', '/charge?loan=L1', b'')]
