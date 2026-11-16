from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest


@pytest.fixture
def payment_gateway(monkeypatch):
    state = {'status': 200, 'body': b'charged\n', 'requests': []}

    class PaymentHandler(BaseHTTPRequestHandler):
        def _respond(self):
            body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
            state['requests'].append((self.command, self.path, body))
            self.send_response(state['status'])
            if state['status'] == 302:
                self.send_header('Location', '/charge?loan=L1')
            self.end_headers()
            self.wfile.write(state['body'])

        def do_GET(self):
            self._respond()

        def do_POST(self):
            self._respond()

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), PaymentHandler)
    thread = Thread(target=server.serve_forever)
    thread.start()
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', f'http://127.0.0.1:{server.server_port}')

    yield state

    server.shutdown()
    thread.join()
    server.server_close()
