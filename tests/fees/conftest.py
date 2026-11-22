from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest


@pytest.fixture
def payment_gateway_server(monkeypatch):
    requests = []
    reply = {'status': 200, 'body': b'charged\n', 'location': None}

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
            requests.append((self.command, self.path, body))
            self.send_response(reply['status'])
            if reply['location']:
                self.send_header('Location', reply['location'])
            self.end_headers()
            self.wfile.write(reply['body'])

        def do_GET(self):
            requests.append((self.command, self.path, b''))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'redirected\n')

        def log_message(self, format, *args):
            return

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = Thread(target=server.serve_forever)
    thread.start()
    base_url = f'http://127.0.0.1:{server.server_port}'
    reply['base_url'] = base_url
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', base_url)

    try:
        yield requests, reply
    finally:
        server.shutdown()
        thread.join()
        server.server_close()
