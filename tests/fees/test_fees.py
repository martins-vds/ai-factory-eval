import logging
import threading
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace

import pytest
from django.utils import timezone
from playwright.sync_api import sync_playwright

from src.loans.models import Loan


@pytest.fixture
def payment_gateway(monkeypatch):
    state = SimpleNamespace(
        body=b'charged\n',
        requests=[],
        status=200,
    )

    class GatewayHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
            state.requests.append((self.command, self.path, body))
            self.send_response(state.status)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(state.body)

        def log_message(self, format, *args):
            return

    server = ThreadingHTTPServer(('127.0.0.1', 0), GatewayHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', f'http://127.0.0.1:{server.server_port}')

    try:
        yield state
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('late_days', 'display_days', 'amount'),
    [
        (-3, 0, '$0.00'),
        (2, 2, '$0.00'),
        (3, 3, '$0.75'),
        (19, 19, '$4.75'),
        (41, 41, '$10.00'),
    ],
)
def test_fee_api_applies_late_day_grace_period_daily_rate_and_cap(
    client, late_days, display_days, amount
):
    due_on = date(2026, 1, 15)
    Loan.objects.create(
        id='F1',
        member='reader',
        isbn='123',
        lent_on=due_on - timedelta(days=14),
        returned_on=due_on + timedelta(days=late_days),
    )

    response = client.get('/fees/F1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == (
        f'<h1>Late fee for F1</h1><p>Due 2026-01-15, {display_days} day(s) late.</p>'
        f'<p class="fee">Fee: {amount}</p>'
    )


@pytest.mark.django_db
def test_fee_api_matches_characterized_fragment(client):
    loan = Loan.objects.get(pk='L3')
    loan.returned_on = date(2026, 1, 3)
    loan.save(update_fields=['returned_on'])

    response = client.get('/fees/L3')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == (
        '<h1>Late fee for L3</h1><p>Due 2025-12-15, 19 day(s) late.</p>'
        '<p class="fee">Fee: $4.75</p>'
    )


@pytest.mark.django_db
def test_fee_api_returns_characterized_not_found_response(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content == b'<p>No such loan.</p>'


@pytest.mark.django_db
def test_fee_page_uses_reading_room_layout_and_htmx_payment_action(client):
    loan = Loan.objects.get(pk='L3')
    loan.returned_on = date(2026, 1, 3)
    loan.save(update_fields=['returned_on'])

    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'Late fee for L3' in response.content
    assert b'Due Dec 15, 2025' in response.content
    assert b'Fee: $4.75' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content
    assert b'hx-target="#payment-status"' in response.content
    assert b'{% csrf_token %}' not in response.content


@pytest.mark.django_db
@pytest.mark.parametrize(('late_days', 'amount'), [(2, '$0.00'), (3, '$0.75')])
def test_fee_api_uses_today_for_unreturned_loans(client, late_days, amount):
    due_on = timezone.localdate() - timedelta(days=late_days)
    Loan.objects.create(
        id='F1',
        member='reader',
        isbn='123',
        lent_on=due_on - timedelta(days=14),
    )

    response = client.get('/fees/F1')

    assert response.status_code == 200
    assert f'{late_days} day(s) late.'.encode() in response.content
    assert f'Fee: {amount}'.encode() in response.content


@pytest.mark.django_db
def test_payment_api_posts_empty_body_and_returns_gateway_success(client, payment_gateway):
    response = client.post('/payments/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'charged\n'
    assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_payment_api_maps_gateway_decline_to_bad_gateway_and_preserves_body(
    client, payment_gateway
):
    payment_gateway.status = 503
    payment_gateway.body = b'declined\n'

    response = client.post('/payments/L2')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'declined\n'
    assert payment_gateway.requests == [('POST', '/charge?loan=L2', b'')]


@pytest.mark.django_db
def test_payment_api_does_not_call_gateway_for_unknown_loan(client, payment_gateway):
    response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'no such loan\n'
    assert payment_gateway.requests == []


@pytest.mark.django_db
def test_payment_api_maps_connection_failure_to_characterized_gateway_failure(client, monkeypatch):
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', 'http://127.0.0.1:1')

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'payment gateway unavailable\n'


@pytest.mark.django_db
def test_payment_api_preserves_interruption_while_returning_gateway_failure(
    client, caplog, monkeypatch
):
    from src.fees import gateway

    class InterruptedOpener:
        def open(self, request):
            raise InterruptedError('gateway call interrupted')

    monkeypatch.setattr(gateway, 'build_opener', lambda *handlers: InterruptedOpener())

    with caplog.at_level(logging.ERROR, logger='src.fees.views'):
        response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'
    assert 'PaymentInterrupted: payment gateway request was interrupted' in caplog.text
    assert 'InterruptedError: gateway call interrupted' in caplog.text


@pytest.mark.django_db
def test_payment_api_uses_configured_default_gateway_url(client, monkeypatch):
    from src.fees import gateway

    class GatewayResponse:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def read(self):
            return b'charged\n'

    class GatewayOpener:
        request = None

        def open(self, request):
            self.request = request
            return GatewayResponse()

    opener = GatewayOpener()
    monkeypatch.delenv('PAYMENT_GATEWAY_URL', raising=False)
    monkeypatch.setattr(gateway, 'build_opener', lambda *handlers: opener)

    response = client.post('/payments/L1')

    assert response.status_code == 200
    assert opener.request.full_url == ('https://payments.lending-library.invalid/charge?loan=L1')
    assert opener.request.get_method() == 'POST'
    assert opener.request.data == b''


@pytest.mark.django_db
def test_ui_payment_updates_htmx_status_after_success(client, payment_gateway):
    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'id="payment-status"' in response.content
    assert b'role="status"' in response.content
    assert b'Payment successful.' in response.content
    assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_regular_ui_payment_renders_full_fee_page_with_status(client, payment_gateway):
    response = client.post('/ui/payments/L1/')

    assert response.status_code == 200
    assert b'<!doctype html>' in response.content
    assert b'Payment successful.' in response.content
    assert b'id="payment-status"' in response.content
    assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_browser_can_pay_late_fee_from_fee_page(live_server, payment_gateway):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/fees/L1/')
            page.get_by_role('button', name='Pay late fee').click()
            status = page.get_by_role('status')
            status.wait_for()

            assert status.inner_text() == 'Payment successful.'
            assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]
        finally:
            browser.close()


@pytest.mark.django_db
def test_ui_payment_updates_htmx_status_after_gateway_failure(client, payment_gateway):
    payment_gateway.status = 503
    payment_gateway.body = b'declined\n'

    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="alert"' in response.content
    assert b'Payment could not be processed.' in response.content


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('path', 'method'),
    [
        ('/fees/L1', 'post'),
        ('/payments/L1', 'get'),
        ('/ui/fees/L1/', 'post'),
        ('/ui/payments/L1/', 'get'),
    ],
)
def test_fee_and_payment_routes_reject_unsupported_methods(client, payment_gateway, path, method):
    response = getattr(client, method)(path)

    assert response.status_code == 405
    assert payment_gateway.requests == []
