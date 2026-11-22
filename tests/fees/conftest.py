from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest


@pytest.fixture
def payment_gateway_server(monkeypatch):
    state = {'status': 200, 'body': b'charged\n', 'requests': []}

    class PaymentGatewayHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
            state['requests'].append((self.command, self.path, body))
            self.send_response(state['status'])
            self.end_headers()
            self.wfile.write(state['body'])

        def log_message(self, format, *args):
            return

    server = ThreadingHTTPServer(('127.0.0.1', 0), PaymentGatewayHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', f'http://127.0.0.1:{server.server_port}')

    yield state

    server.shutdown()
    thread.join()
    server.server_close()
