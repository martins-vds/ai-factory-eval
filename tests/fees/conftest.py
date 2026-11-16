from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from types import SimpleNamespace
from urllib.parse import parse_qs, urlsplit

import pytest


@pytest.fixture
def payment_gateway():
    requests = []
    responses = {
        'L1': (200, b'charged\n'),
        'L2': (503, b'declined\n'),
    }

    class GatewayHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
            requests.append((self.command, self.path, body))
            loan_id = parse_qs(urlsplit(self.path).query).get('loan', [''])[0]
            status, response_body = responses.get(loan_id, (200, b'charged\n'))
            self.send_response(status)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(response_body)

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), GatewayHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    gateway = SimpleNamespace(
        url=f'http://127.0.0.1:{server.server_port}',
        requests=requests,
        responses=responses,
    )
    try:
        yield gateway
    finally:
        server.shutdown()
        thread.join()
        server.server_close()
