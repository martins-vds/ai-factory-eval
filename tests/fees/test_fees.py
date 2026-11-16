from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import date
from threading import Thread

import pytest
from django.test import override_settings

from src.fees.gateway import HttpPaymentGateway, PaymentGatewayUnavailable
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
def test_fee_endpoint_charges_each_late_day_after_grace_period(client):
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
        '<p class="fee">Fee: $0.75</p>'
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('late_days', 'expected_fee'),
    [
        (-1, '$0.00'),
        (2, '$0.00'),
        (3, '$0.75'),
        (39, '$9.75'),
        (40, '$10.00'),
        (41, '$10.00'),
        (100, '$10.00'),
    ],
)
def test_fee_endpoint_applies_grace_period_and_cap(client, late_days, expected_fee):
    due_on = date(2026, 1, 1)
    Loan.objects.create(
        id=f'F{late_days}',
        member='reader',
        isbn='123',
        lent_on=date(2025, 12, 18),
        returned_on=date.fromordinal(due_on.toordinal() + late_days),
    )

    response = client.get(f'/fees/F{late_days}')

    assert response.status_code == 200
    assert f'Fee: {expected_fee}'.encode() in response.content


@pytest.mark.django_db
def test_fee_endpoint_returns_characterized_not_found_response(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content == b'<p>No such loan.</p>'


@pytest.mark.django_db
def test_fee_page_shows_quote_and_htmx_payment_action(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'<title>Late fee for L3' in response.content
    assert b'Late fee for L3</h1>' in response.content
    assert b'Dec 15, 2025' in response.content
    assert b'19 day(s) late' in response.content
    fee_line = next(
        line for line in response.content.decode().splitlines() if 'class="fee mt-6' in line
    )
    assert 'Fee: $4.75' in fee_line, fee_line
    assert b'hx-post="/ui/payments/L3/"' in response.content


@pytest.mark.django_db
def test_htmx_payment_action_returns_gateway_success_fragment(client, payment_gateway):
    with override_settings(PAYMENT_GATEWAY_URL=payment_gateway.url):
        response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'<html' not in response.content
    assert b'role="status"' in response.content
    assert b'charged' in response.content
    assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_payment_endpoint_forwards_gateway_request_and_success_body(client, payment_gateway):
    with override_settings(PAYMENT_GATEWAY_URL=payment_gateway.url):
        response = client.post('/payments/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'charged\n'
    assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_payment_endpoint_maps_non_200_gateway_response_to_502(client, payment_gateway):
    payment_gateway.response_status = 503
    payment_gateway.response_body = b'declined\n'

    with override_settings(PAYMENT_GATEWAY_URL=payment_gateway.url):
        response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'declined\n'
    assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_payment_endpoint_does_not_call_gateway_for_unknown_loan(client, payment_gateway):
    with override_settings(PAYMENT_GATEWAY_URL=payment_gateway.url):
        response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'no such loan\n'
    assert payment_gateway.requests == []


@pytest.mark.django_db
def test_payment_endpoint_maps_io_failure_to_gateway_unavailable(client):
    with override_settings(PAYMENT_GATEWAY_URL='http://127.0.0.1:1'):
        response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'payment gateway unavailable\n'


def test_payment_gateway_preserves_interruption_as_failure_cause(monkeypatch):
    interruption = InterruptedError('gateway call interrupted')

    def interrupt(*args, **kwargs):
        raise interruption

    monkeypatch.setattr('src.fees.gateway.urlopen', interrupt)

    with pytest.raises(PaymentGatewayUnavailable) as failure:
        HttpPaymentGateway().charge('L1')

    assert failure.value.__cause__ is interruption
