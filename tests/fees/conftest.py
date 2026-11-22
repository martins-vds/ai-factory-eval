from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest


class PaymentServer(ThreadingHTTPServer):
    def __init__(self):
        super().__init__(('127.0.0.1', 0), PaymentHandler)
        self.requests = []
        self.response_status = 200
        self.response_body = b'charged\n'


class PaymentHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.server.requests.append(
            (self.command, self.path, self.rfile.read(int(self.headers.get('Content-Length', 0))))
        )
        self.send_response(self.server.response_status)
        self.end_headers()
        self.wfile.write(self.server.response_body)

    def log_message(self, format, *args):
        pass


@pytest.fixture
def payment_server():
    server = PaymentServer()
    thread = Thread(target=server.serve_forever)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        thread.join()
        server.server_close()
