from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest


@pytest.fixture
def gateway_server():
    requests = []

    class Handler(BaseHTTPRequestHandler):
        response_status = 200
        response_body = b'charged\n'

        def do_POST(self):
            body = self.rfile.read(int(self.headers.get('Content-Length', '0')))
            requests.append((self.command, self.path, body))
            self.send_response(self.response_status)
            self.end_headers()
            self.wfile.write(self.response_body)

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = Thread(target=server.serve_forever)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}', Handler, requests
    finally:
        server.shutdown()
        thread.join()
        server.server_close()
