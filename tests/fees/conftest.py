from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest


@pytest.fixture
def payment_gateway_server(monkeypatch):
    state = {'status': 200, 'body': b'charged\n', 'redirect_to': None, 'requests': []}

    class PaymentGatewayHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
            state['requests'].append((self.command, self.path, body))
            self.send_response(state['status'])
            if state['redirect_to']:
                self.send_header('Location', state['redirect_to'])
            self.end_headers()
            self.wfile.write(state['body'])

        def do_GET(self):
            state['requests'].append((self.command, self.path, b''))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'redirected success\n')

        def log_message(self, format, *args):
            return

    server = ThreadingHTTPServer(('127.0.0.1', 0), PaymentGatewayHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    state['base_url'] = f'http://127.0.0.1:{server.server_port}'
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', state['base_url'])

    yield state

    server.shutdown()
    thread.join()
    server.server_close()
