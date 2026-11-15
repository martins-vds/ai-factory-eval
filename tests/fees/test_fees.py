from datetime import date, timedelta
from decimal import Decimal
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest
from playwright.sync_api import sync_playwright

from src.fees.services import calculate_late_fee


@pytest.fixture
def payment_gateway():
    requests = []

    class GatewayHandler(BaseHTTPRequestHandler):
        response_status = 200
        response_body = b'charged\n'
        response_headers = None

        def do_POST(self):
            requests.append(
                (self.command, self.path, self.rfile.read(int(self.headers['Content-Length'] or 0)))
            )
            self.send_response(self.response_status)
            self.send_header('Content-Type', 'text/plain')
            for name, value in (self.response_headers or {}).items():
                self.send_header(name, value)
            self.end_headers()
            self.wfile.write(self.response_body)

        def log_message(self, format, *args):
            return

    server = ThreadingHTTPServer(('127.0.0.1', 0), GatewayHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f'http://127.0.0.1:{server.server_port}', requests, GatewayHandler
    server.shutdown()
    server.server_close()
    thread.join()


def test_late_fee_charges_twenty_five_cents_per_day_after_grace_threshold():
    fee = calculate_late_fee(
        due_on=date(2026, 11, 12),
        returned_on=None,
        today=date(2026, 11, 15),
    )

    assert fee.days_late == 3
    assert fee.amount == Decimal('0.75')


def test_late_fee_matches_characterized_nineteen_day_amount():
    fee = calculate_late_fee(
        due_on=date(2025, 12, 15),
        returned_on=date(2026, 1, 3),
        today=date(2026, 11, 15),
    )

    assert fee.days_late == 19
    assert fee.amount == Decimal('4.75')


@pytest.mark.parametrize(
    ('days_late', 'expected_amount'),
    [
        (0, Decimal('0.00')),
        (2, Decimal('0.00')),
        (50, Decimal('10.00')),
    ],
)
def test_late_fee_applies_grace_period_and_ten_dollar_cap(days_late, expected_amount):
    due_on = date(2026, 11, 1)
    fee = calculate_late_fee(
        due_on=due_on,
        returned_on=None,
        today=due_on + timedelta(days=days_late),
    )

    assert fee.days_late == days_late
    assert fee.amount == expected_amount


@pytest.mark.django_db
def test_fee_api_returns_characterized_html_for_a_known_loan(client):
    response = client.get('/fees/L3')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == (
        '<h1>Late fee for L3</h1><p>Due 2025-12-15, 19 day(s) late.</p>'
        '<p class="fee">Fee: $4.75</p>'
    )


@pytest.mark.django_db
def test_fee_api_returns_characterized_not_found_response_for_unknown_loan(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content == b'<p>No such loan.</p>'


@pytest.mark.django_db
def test_payment_api_posts_to_the_gateway_and_forwards_success(
    client, monkeypatch, payment_gateway
):
    gateway_url, requests, _ = payment_gateway
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

    response = client.post('/payments/L3')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'charged\n'
    assert requests == [('POST', '/charge?loan=L3', b'')]


@pytest.mark.django_db
def test_payment_api_maps_gateway_failures_to_bad_gateway_and_keeps_body(
    client, monkeypatch, payment_gateway
):
    gateway_url, _, handler = payment_gateway
    handler.response_status = 503
    handler.response_body = b'declined\n'
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

    response = client.post('/payments/L3')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'declined\n'


@pytest.mark.django_db
def test_payment_api_does_not_follow_gateway_redirects(client, monkeypatch, payment_gateway):
    gateway_url, requests, handler = payment_gateway
    handler.response_status = 302
    handler.response_body = b'redirected\n'
    handler.response_headers = {'Location': 'http://127.0.0.1:9/charge'}
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

    response = client.post('/payments/L3')

    assert response.status_code == 502
    assert response.content == b'redirected\n'
    assert requests == [('POST', '/charge?loan=L3', b'')]


@pytest.mark.django_db
def test_payment_api_does_not_call_gateway_for_an_unknown_loan(
    client, monkeypatch, payment_gateway
):
    gateway_url, requests, _ = payment_gateway
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

    response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response.content == b'no such loan\n'
    assert requests == []


@pytest.mark.django_db
def test_interrupted_payment_is_a_gateway_failure_without_losing_cause(client, caplog, monkeypatch):
    def interrupt(request):
        raise InterruptedError('gateway request interrupted')

    monkeypatch.setattr('src.fees.gateway.open_url', interrupt)

    response = client.post('/payments/L3')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'
    failure = next(
        record for record in caplog.records if record.message == 'Payment gateway call interrupted'
    )
    assert isinstance(failure.exc_info[1].__cause__, InterruptedError)


@pytest.mark.django_db
def test_fee_page_uses_reading_room_layout_and_has_htmx_payment_action(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'A small nudge, never a surprise' in response.content
    assert b'19 late days' in response.content
    assert b'$4.75' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content


@pytest.mark.django_db
def test_htmx_payment_action_reports_gateway_success(client, monkeypatch, payment_gateway):
    gateway_url, requests, _ = payment_gateway
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

    response = client.post('/ui/payments/L3/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="status"' in response.content
    assert b'Payment received.' in response.content
    assert requests == [('POST', '/charge?loan=L3', b'')]


@pytest.mark.django_db
def test_regular_payment_action_redirects_to_the_fee_page(client, monkeypatch, payment_gateway):
    gateway_url, _, _ = payment_gateway
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

    response = client.post('/ui/payments/L3/')

    assert response.status_code == 302
    assert response['Location'] == '/ui/fees/L3/?payment=success'


@pytest.mark.django_db
def test_htmx_payment_action_keeps_gateway_failures_visible(client, monkeypatch, payment_gateway):
    gateway_url, _, handler = payment_gateway
    handler.response_status = 503
    handler.response_body = b'declined\n'
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

    response = client.post('/ui/payments/L3/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="alert"' in response.content
    assert b'declined' in response.content


@pytest.mark.django_db
def test_unknown_fee_page_returns_characterized_not_found_fragment(client):
    response = client.get('/ui/fees/unknown/')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content == b'<p>No such loan.</p>'


@pytest.mark.django_db
def test_browser_can_pay_a_late_fee_from_the_reading_room_page(
    live_server, monkeypatch, payment_gateway
):
    gateway_url, requests, _ = payment_gateway
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/fees/L3/')
            assert page.get_by_role('heading', name='Late fees').is_visible()

            htmx_available = page.evaluate("typeof window.htmx !== 'undefined'")
            page.get_by_role('button', name='Pay fee').click()
            if htmx_available:
                page.get_by_role('status').wait_for()
            else:
                page.wait_for_url('**/ui/fees/L3/?payment=success')

            assert page.get_by_role('status').inner_text() == 'Payment received.'
            assert requests == [('POST', '/charge?loan=L3', b'')]
        finally:
            browser.close()
