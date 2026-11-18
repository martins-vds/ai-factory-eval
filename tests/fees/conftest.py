import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace

import pytest


@pytest.fixture
def gateway_server(monkeypatch):
    received = []
    responses = []

    class GatewayHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            received.append(
                {
                    'method': self.command,
                    'path': self.path,
                    'body': self.rfile.read(int(self.headers.get('Content-Length', 0))).decode(),
                }
            )
            status, body = responses.pop(0) if responses else (200, 'charged\n')
            self.send_response(status)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(body.encode())

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), GatewayHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', f'http://127.0.0.1:{server.server_port}')
    yield SimpleNamespace(received=received, responses=responses)
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)
