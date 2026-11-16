from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import date
from threading import Thread

import pytest
from django.test import override_settings

from src.loans.models import Loan


@pytest.fixture
def payment_gateway():
    class GatewayHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = self.rfile.read(int(self.headers.get('Content-Length', '0')))
            self.server.requests.append((self.command, self.path, body))
            self.send_response(self.server.response_status)
            self.end_headers()
            self.wfile.write(self.server.response_body)

        def log_message(self, format, *args):
            return

    server = ThreadingHTTPServer(('127.0.0.1', 0), GatewayHandler)
    server.requests = []
    server.response_status = 200
    server.response_body = b'charged\n'
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    server.url = f'http://127.0.0.1:{server.server_port}'
    try:
        yield server
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


@pytest.mark.django_db
def test_fee_endpoint_charges_twenty_five_cents_after_two_day_grace_period(client):
    Loan.objects.create(
        id='F1',
        member='reader',
        isbn='123',
        lent_on=date(2025, 12, 18),
        returned_on=date(2026, 1, 4),
    )

    response = client.get('/fees/F1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == (
        '<h1>Late fee for F1</h1><p>Due 2026-01-01, 3 day(s) late.</p>'
        '<p class="fee">Fee: $0.25</p>'
    )


@pytest.mark.django_db
def test_payment_endpoint_forwards_gateway_request_and_success_body(client, payment_gateway):
    with override_settings(PAYMENT_GATEWAY_URL=payment_gateway.url):
        response = client.post('/payments/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'charged\n'
    assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]
