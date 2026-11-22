from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest


@pytest.fixture
def gateway_server():
    servers = []

    def start(status, body):
        requests = []

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                length = int(self.headers.get('Content-Length', 0))
                requests.append((self.command, self.path, self.rfile.read(length)))
                self.send_response(status)
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format, *args):
                pass

        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = Thread(target=server.serve_forever)
        thread.start()
        servers.append((server, thread))
        return f'http://127.0.0.1:{server.server_port}', requests

    yield start

    for server, thread in servers:
        server.shutdown()
        thread.join()
        server.server_close()
