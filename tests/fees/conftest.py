from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest


@pytest.fixture
def payment_gateway(monkeypatch):
    requests = []

    class GatewayHandler(BaseHTTPRequestHandler):
        def _handle_request(self):
            body_length = int(self.headers['Content-Length'] or 0)
            requests.append((self.command, self.path, self.rfile.read(body_length)))
            headers = {}
            if self.path.endswith('L2'):
                status, body = 503, b'declined\n'
            elif self.path.endswith('L3'):
                status, body = 302, b'redirected\n'
                headers = {'Location': '/redirect'}
            elif self.path == '/redirect':
                status, body = 200, b'followed redirect\n'
            else:
                status, body = 200, b'charged\n'
            self.send_response(status)
            for name, value in headers.items():
                self.send_header(name, value)
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            self._handle_request()

        def do_POST(self):
            self._handle_request()

        def log_message(self, format, *args):
            return

    server = ThreadingHTTPServer(('127.0.0.1', 0), GatewayHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', f'http://127.0.0.1:{server.server_port}')
    server.requests = requests
    try:
        yield server
    finally:
        server.shutdown()
        thread.join()
        server.server_close()
