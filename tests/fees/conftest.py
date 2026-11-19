from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from typing import ClassVar

import pytest


@pytest.fixture
def local_gateway():
    class Handler(BaseHTTPRequestHandler):
        requests: ClassVar[list[tuple[str, str, bytes]]] = []

        def do_POST(self):
            body = self.rfile.read(int(self.headers.get('Content-Length', '0')))
            self.requests.append((self.command, self.path, body))
            if self.path.endswith('loan=L3'):
                self.send_response(302)
                self.send_header('Location', f'http://{self.headers["Host"]}/charge?loan=L1')
                self.end_headers()
                return
            if self.path.endswith('loan=L1'):
                self.send_response(200)
                response_body = b'charged\n'
            else:
                self.send_response(503)
                response_body = b'declined\n'
            self.end_headers()
            self.wfile.write(response_body)

        def do_GET(self):
            self.requests.append((self.command, self.path, b''))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'redirected\n')

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}', Handler.requests
    finally:
        server.shutdown()
        thread.join()
        server.server_close()
