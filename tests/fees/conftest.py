import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest


class PaymentGatewayHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
        self.server.requests.append((self.command, self.path, body))
        response = self.server.response_body
        self.send_response(self.server.response_status)
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, format, *args):
        return


@pytest.fixture
def payment_gateway(monkeypatch):
    server = ThreadingHTTPServer(('127.0.0.1', 0), PaymentGatewayHandler)
    server.requests = []
    server.response_status = 200
    server.response_body = b'charged\n'
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', f'http://127.0.0.1:{server.server_port}')

    yield server

    server.shutdown()
    server.server_close()
    thread.join()
