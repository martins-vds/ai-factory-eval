from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from typing import ClassVar

import pytest


@pytest.fixture
def payment_gateway():
    class Gateway:
        status = 200
        body = b'charged\n'
        requests: ClassVar[list] = []

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                length = int(self.headers.get('Content-Length', 0))
                Gateway.requests.append((self.command, self.path, self.rfile.read(length)))
                self.send_response(Gateway.status)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(Gateway.body)

            def log_message(self, _format, *_args):
                pass

    Gateway.requests = []
    server = ThreadingHTTPServer(('127.0.0.1', 0), Gateway.Handler)
    thread = Thread(target=server.serve_forever)
    thread.start()
    Gateway.url = f'http://127.0.0.1:{server.server_port}'
    try:
        yield Gateway
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
