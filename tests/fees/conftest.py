from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest


@pytest.fixture
def payment_gateway(monkeypatch):
    requests = []

    class GatewayHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            requests.append((self.command, self.path, self.rfile.read(int(self.headers['Content-Length'] or 0))))
            status, body = (503, b'declined\n') if self.path.endswith('L2') else (200, b'charged\n')
            self.send_response(status)
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

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
