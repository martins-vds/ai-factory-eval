from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest


@pytest.fixture
def payment_gateway_server(monkeypatch):
    received = []
    configured_response = {'status': 200, 'body': b'charged\n', 'headers': {}}

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
            received.append((self.command, self.path, body))
            self.send_response(configured_response['status'])
            for name, value in configured_response['headers'].items():
                self.send_header(name, value)
            self.end_headers()
            self.wfile.write(configured_response['body'])

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = Thread(target=server.serve_forever)
    thread.start()
    monkeypatch.setenv(
        'PAYMENT_GATEWAY_URL',
        f'http://127.0.0.1:{server.server_port}',
    )
    try:
        yield received, configured_response, server.server_port
    finally:
        server.shutdown()
        thread.join()
        server.server_close()
