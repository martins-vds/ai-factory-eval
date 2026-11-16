from contextlib import contextmanager
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest
from django.utils import timezone
from playwright.sync_api import sync_playwright

from src.loans.models import Loan


@contextmanager
def local_gateway(status, body):
    requests = []

    class GatewayHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get('Content-Length', 0))
            requests.append(
                ('POST', self.path, self.rfile.read(length))
            )
            self.send_response(status)
            if status == 302:
                self.send_header('Location', '/redirected')
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            requests.append(('GET', self.path, b''))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'redirected\n')

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), GatewayHandler)
    thread = Thread(target=server.serve_forever)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}', requests
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


@pytest.mark.django_db
def test_fee_endpoint_renders_the_characterized_loan_fee(client):
    response = client.get('/fees/L3')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == (
        '<h1>Late fee for L3</h1><p>Due 2025-12-15, 19 day(s) late.</p>'
        '<p class="fee">Fee: $4.75</p>'
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('returned_on', 'expected_days', 'expected_fee'),
    [
        (date(2026, 3, 14), 0, '0.00'),
        (date(2026, 3, 16), 1, '0.00'),
        (date(2026, 3, 17), 2, '0.00'),
        (date(2026, 3, 18), 3, '0.75'),
        (date(2026, 4, 24), 40, '10.00'),
    ],
)
def test_fee_endpoint_applies_grace_period_and_cap(
    client, returned_on, expected_days, expected_fee
):
    Loan.objects.create(
        id='F1',
        member='reader',
        isbn='123',
        lent_on=date(2026, 3, 1),
        returned_on=returned_on,
    )

    response = client.get('/fees/F1')

    assert response.status_code == 200
    assert f'{expected_days} day(s) late.'.encode() in response.content
    assert f'Fee: ${expected_fee}'.encode() in response.content


@pytest.mark.django_db
def test_unreturned_fee_uses_the_server_local_date(client):
    today = timezone.localdate()
    Loan.objects.create(
        id='F2',
        member='reader',
        isbn='123',
        lent_on=today - timedelta(days=17),
    )

    response = client.get('/fees/F2')

    assert response.status_code == 200
    assert b'3 day(s) late.' in response.content
    assert b'Fee: $0.75' in response.content


@pytest.mark.django_db
def test_fee_endpoint_returns_the_characterized_missing_loan_response(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content == b'<p>No such loan.</p>'


@pytest.mark.django_db
def test_fee_page_uses_reading_room_layout_and_offers_htmx_payment(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'The Lending Library' in response.content
    assert b'Late fee for L3' in response.content
    assert b'Fee: $4.75' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content
    assert b'action="/ui/payments/L3/"' in response.content


@pytest.mark.django_db
def test_payment_endpoint_forwards_the_gateway_request(client, monkeypatch):
    with local_gateway(200, b'charged\n') as (gateway_url, requests):
        monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

        response = client.post('/payments/L3')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'charged\n'
    assert requests == [('POST', '/charge?loan=L3', b'')]


@pytest.mark.django_db
@pytest.mark.parametrize('status', [201, 302, 503])
def test_non_200_gateway_responses_become_bad_gateway(client, monkeypatch, status):
    with local_gateway(status, b'declined\n') as (gateway_url, requests):
        monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

        response = client.post('/payments/L3')

    assert response.status_code == 502
    assert response.content == b'declined\n'
    assert requests == [('POST', '/charge?loan=L3', b'')]


@pytest.mark.django_db
def test_payment_endpoint_does_not_call_gateway_for_an_unknown_loan(client, monkeypatch):
    with local_gateway(200, b'charged\n') as (gateway_url, requests):
        monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

        response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'no such loan\n'
    assert requests == []


@pytest.mark.django_db
def test_fee_page_payment_returns_an_htmx_status(client, monkeypatch):
    with local_gateway(200, b'charged\n') as (gateway_url, requests):
        monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

        response = client.post(
            '/ui/payments/L3/',
            HTTP_HX_REQUEST='true',
        )

    assert response.status_code == 200
    assert b'id="payment-status"' in response.content
    assert b'role="status"' in response.content
    assert b'charged' in response.content
    assert requests == [('POST', '/charge?loan=L3', b'')]


@pytest.mark.django_db
def test_fee_page_payment_shows_gateway_failure_in_htmx(client, monkeypatch):
    with local_gateway(503, b'<p>declined</p>') as (gateway_url, requests):
        monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

        response = client.post(
            '/ui/payments/L3/',
            HTTP_HX_REQUEST='true',
        )

    assert response.status_code == 200
    assert b'role="alert"' in response.content
    assert b'&lt;p&gt;declined&lt;/p&gt;' in response.content
    assert requests == [('POST', '/charge?loan=L3', b'')]


@pytest.mark.django_db
def test_real_browser_can_pay_a_late_fee(live_server, monkeypatch):
    with local_gateway(200, b'charged\n') as (gateway_url, requests):
        monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                page = browser.new_page()
                page.goto(f'{live_server.url}/ui/fees/L3/')
                assert page.get_by_role('heading', name='Late fee for L3').is_visible()
                page.get_by_role('button', name='Pay late fee').click()
                page.get_by_role('status').wait_for()
                assert page.get_by_role('status').inner_text() == 'charged'
            finally:
                browser.close()

    assert requests == [('POST', '/charge?loan=L3', b'')]


@pytest.mark.django_db
def test_interrupted_payment_is_a_gateway_failure_and_remains_visible(
    client, monkeypatch, caplog
):
    def interrupt(_request):
        raise InterruptedError('gateway interrupted')

    monkeypatch.setattr('src.fees.services._open_gateway', interrupt)

    with caplog.at_level('ERROR'):
        response = client.post('/payments/L3')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'
    assert 'InterruptedError' in caplog.text
