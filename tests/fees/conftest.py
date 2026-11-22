from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest


@pytest.fixture
def payment_gateway_server(monkeypatch):
    requests = []
    reply = {'status': 200, 'body': b'charged\n'}

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
            requests.append((self.command, self.path, body))
            self.send_response(reply['status'])
            self.end_headers()
            self.wfile.write(reply['body'])

        def log_message(self, format, *args):
            return

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = Thread(target=server.serve_forever)
    thread.start()
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', f'http://127.0.0.1:{server.server_port}')

    try:
        yield requests, reply
    finally:
        server.shutdown()
        thread.join()
        server.server_close()
