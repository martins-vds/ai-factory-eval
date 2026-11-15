from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest

from src.fees.gateway import HttpPaymentGateway, PaymentGatewayUnavailable
from src.loans.models import Loan


@pytest.fixture
def local_gateway(monkeypatch):
    requests = []

    class GatewayHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            requests.append((self.command, self.path, self.rfile.read(int(self.headers.get('Content-Length', 0)))))
            status, body = (503, b'declined\n') if self.path.endswith('loan=L2') else (200, b'charged\n')
            self.send_response(status)
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), GatewayHandler)
    thread = Thread(target=server.serve_forever)
    thread.start()
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', f'http://127.0.0.1:{server.server_port}')
    yield requests
    server.shutdown()
    server.server_close()
    thread.join()


@pytest.mark.django_db
def test_fee_api_returns_characterized_html_for_a_returned_loan(client):
    response = client.get('/fees/L3')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == (
        '<h1>Late fee for L3</h1>'
        '<p>Due 2025-12-15, 19 day(s) late.</p>'
        '<p class="fee">Fee: $4.75</p>'
    )


@pytest.mark.django_db
def test_fee_page_shows_amount_and_htmx_payment_action(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'Late fee for L3</h1>' in response.content
    assert b'19 day(s) late' in response.content
    assert b'$4.75' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content


@pytest.mark.django_db
def test_payment_api_posts_to_gateway_and_forwards_success(client, local_gateway):
    response = client.post('/payments/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'charged\n'
    assert local_gateway == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('loan_id', 'returned_on', 'expected_days', 'expected_fee'),
    [
        ('FEE2', date(2026, 1, 18), '2 day(s) late', '$0.00'),
        ('FEE3', date(2026, 1, 19), '3 day(s) late', '$0.75'),
        ('FEECAP', date(2026, 3, 1), '44 day(s) late', '$10.00'),
    ],
)
def test_fee_api_applies_grace_period_and_cap(
    client, loan_id, returned_on, expected_days, expected_fee
):
    Loan.objects.create(
        id=loan_id,
        member='reader',
        isbn='123',
        lent_on=date(2026, 1, 2),
        returned_on=returned_on,
    )

    response = client.get(f'/fees/{loan_id}')

    assert response.status_code == 200
    body = response.content.decode()
    assert f', {expected_days}.' in body
    assert expected_fee in body


@pytest.mark.django_db
def test_fee_api_returns_characterized_not_found_response(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content == b'<p>No such loan.</p>'


@pytest.mark.django_db
def test_payment_api_maps_gateway_failure_to_bad_gateway(client, local_gateway):
    response = client.post('/payments/L2')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'declined\n'
    assert local_gateway == [('POST', '/charge?loan=L2', b'')]


@pytest.mark.django_db
def test_payment_for_unknown_loan_does_not_call_gateway(client, local_gateway):
    response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response.content == b'no such loan\n'
    assert local_gateway == []


@pytest.mark.django_db
def test_payment_api_maps_connection_failure_to_unavailable(client, monkeypatch):
    unavailable_server = ThreadingHTTPServer(('127.0.0.1', 0), BaseHTTPRequestHandler)
    gateway_url = f'http://127.0.0.1:{unavailable_server.server_port}'
    unavailable_server.server_close()
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'payment gateway unavailable\n'


@pytest.mark.django_db
def test_htmx_payment_shows_gateway_success(client, local_gateway):
    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="status"' in response.content
    assert b'Payment complete. charged' in response.content
    assert local_gateway == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_htmx_payment_surfaces_gateway_failure(client, local_gateway):
    response = client.post('/ui/payments/L2/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="alert"' in response.content
    assert b'Payment could not be completed. declined' in response.content


def test_payment_gateway_keeps_interrupted_error_as_cause(monkeypatch):
    def interrupt(request):
        raise InterruptedError('request interrupted')

    monkeypatch.setattr('src.fees.gateway.urlopen', interrupt)
    gateway = HttpPaymentGateway('http://127.0.0.1:1')

    with pytest.raises(PaymentGatewayUnavailable) as failure:
        gateway.charge('L1')

    assert isinstance(failure.value.__cause__, InterruptedError)
