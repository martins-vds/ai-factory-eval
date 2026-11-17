import importlib
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace

import pytest
from django.apps import apps
from django.db import connection


@pytest.fixture(scope='module')
def restore_seed_loans(django_db_blocker):
    yield
    with django_db_blocker.unblock():
        apps.get_model('loans', 'Loan').objects.all().delete()
        seed_loans = importlib.import_module('src.loans.migrations.0001_initial').seed_loans
        with connection.schema_editor() as schema_editor:
            seed_loans(apps, schema_editor)


@pytest.fixture
def payment_gateway(monkeypatch):
    gateway = SimpleNamespace(
        body=b'charged\n',
        requests=[],
        status=200,
        url=None,
        server=None,
        thread=None,
    )

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode()
            gateway.requests.append((self.command, self.path, body))
            self.send_response(gateway.status)
            self.end_headers()
            self.wfile.write(gateway.body)

        def log_message(self, _format, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    gateway.server = server
    gateway.thread = thread
    gateway.url = f'http://127.0.0.1:{server.server_port}'
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway.url)

    def stop():
        if gateway.server is not None:
            gateway.server.shutdown()
            gateway.thread.join()
            gateway.server.server_close()
            gateway.server = None

    gateway.stop = stop
    try:
        yield gateway
    finally:
        stop()
