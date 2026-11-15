from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import date, timedelta
from decimal import Decimal
from threading import Thread

import pytest

from src.fees.gateway import PaymentGateway, PaymentGatewayError
from src.fees.services import calculate_late_fee


@pytest.fixture
def payment_gateway(monkeypatch):
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = self.rfile.read(int(self.headers.get('Content-Length', '0')))
            self.server.requests.append((self.command, self.path, body))
            self.send_response(self.server.response_status)
            self.end_headers()
            self.wfile.write(self.server.response_body)

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    server.requests = []
    server.response_status = 200
    server.response_body = b'charged\n'
    thread = Thread(target=server.serve_forever)
    thread.start()
    monkeypatch.setenv(
        'PAYMENT_GATEWAY_URL',
        f'http://127.0.0.1:{server.server_port}',
    )
    yield server
    server.shutdown()
    thread.join()
    server.server_close()


@pytest.mark.parametrize(
    ('days_late', 'expected_amount'),
    [
        (-3, Decimal('0.00')),
        (0, Decimal('0.00')),
        (1, Decimal('0.00')),
        (2, Decimal('0.00')),
        (3, Decimal('0.75')),
        (40, Decimal('10.00')),
        (100, Decimal('10.00')),
    ],
)
def test_late_fee_uses_two_day_grace_and_caps_at_ten_dollars(days_late, expected_amount):
    due_on = date(2026, 1, 1)

    fee = calculate_late_fee(due_on, due_on + timedelta(days=days_late))

    assert fee.days_late == max(0, days_late)
    assert fee.amount == expected_amount


@pytest.mark.django_db
def test_fee_endpoint_matches_the_characterized_html(client):
    response = client.get('/fees/L3')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == (
        '<h1>Late fee for L3</h1><p>Due 2025-12-15, 19 day(s) late.</p>'
        '<p class="fee">Fee: $4.75</p>'
    )


@pytest.mark.django_db
def test_fee_endpoint_returns_the_characterized_not_found_response(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content == b'<p>No such loan.</p>'


@pytest.mark.django_db
def test_browser_fee_page_uses_reading_room_layout_and_offers_htmx_payment(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'A small nudge, never a surprise' in response.content
    assert b'Late fees' in response.content
    assert b'Due Dec 15, 2025' in response.content
    assert b'19 late days' in response.content
    assert b'first two days waived' in response.content
    assert b'$4.75' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content
    assert b'action="/ui/payments/L3/"' in response.content


@pytest.mark.django_db
def test_payment_endpoint_forwards_the_characterized_gateway_request(client, payment_gateway):
    response = client.post('/payments/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'charged\n'
    assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_payment_endpoint_maps_gateway_failure_to_502_and_preserves_body(
    client, payment_gateway
):
    payment_gateway.response_status = 503
    payment_gateway.response_body = b'declined\n'

    response = client.post('/payments/L2')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'declined\n'


@pytest.mark.django_db
def test_payment_endpoint_does_not_call_gateway_for_unknown_loan(client, payment_gateway):
    response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'no such loan\n'
    assert payment_gateway.requests == []


def test_interrupted_gateway_request_is_preserved_as_the_gateway_error_cause(monkeypatch):
    def interrupted(_request):
        raise InterruptedError('request interrupted')

    monkeypatch.setattr('src.fees.gateway.urlopen', interrupted)

    with pytest.raises(PaymentGatewayError) as error:
        PaymentGateway().charge('L1')

    assert isinstance(error.value.__cause__, InterruptedError)
