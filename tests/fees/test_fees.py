import importlib
import threading
import urllib.request
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
from django.apps import apps
from django.db import connection
from django.utils import timezone
from playwright.sync_api import sync_playwright

from src.loans.models import Loan


@pytest.fixture
def restore_seed_loans(django_db_blocker):
    yield
    with django_db_blocker.unblock():
        Loan.objects.all().delete()
        seed_loans = importlib.import_module('src.loans.migrations.0001_initial').seed_loans
        with connection.schema_editor() as schema_editor:
            seed_loans(apps, schema_editor)


@pytest.fixture
def payment_gateway(monkeypatch):
    class GatewayHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
            self.server.requests.append((self.command, self.path, body))
            self.send_response(self.server.response_status)
            if self.server.response_status == 302:
                self.send_header('Location', '/redirected')
            self.send_header('Content-Length', str(len(self.server.response_body)))
            self.end_headers()
            self.wfile.write(self.server.response_body)

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), GatewayHandler)
    server.requests = []
    server.response_status = 200
    server.response_body = b'charged\n'
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', f'http://127.0.0.1:{server.server_port}')
    yield server
    server.shutdown()
    server.server_close()
    thread.join()


@pytest.mark.django_db
def test_fee_api_matches_characterized_response(client):
    response = client.get('/fees/L3')

    assert response.status_code == 200
    assert response['Content-Type'].startswith('text/html')
    assert response.content.decode() == (
        '<h1>Late fee for L3</h1><p>Due 2025-12-15, 19 day(s) late.</p>'
        '<p class="fee">Fee: $4.75</p>'
    )


@pytest.mark.django_db
def test_fee_api_returns_characterized_not_found_response(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response['Content-Type'].startswith('text/html')
    assert response.content == b'<p>No such loan.</p>'


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('late_days', 'expected_days', 'expected_fee'),
    [
        (-4, 0, '0.00'),
        (2, 2, '0.00'),
        (3, 3, '0.75'),
        (41, 41, '10.00'),
    ],
)
def test_fee_calculation_clamps_grace_period_and_cap(
    client, late_days, expected_days, expected_fee
):
    due_on = date(2026, 1, 15)
    loan = Loan.objects.create(
        id=f'F{late_days + 10}',
        member='reader',
        isbn='123',
        lent_on=due_on - timedelta(days=14),
        returned_on=due_on + timedelta(days=late_days),
    )

    response = client.get(f'/fees/{loan.id}')

    assert response.status_code == 200
    assert response.content.decode() == (
        f'<h1>Late fee for {loan.id}</h1><p>Due {due_on.isoformat()}, '
        f'{expected_days} day(s) late.</p><p class="fee">Fee: ${expected_fee}</p>'
    )


@pytest.mark.django_db
def test_unreturned_fee_uses_the_current_local_date(client):
    today = timezone.localdate()
    due_on = today - timedelta(days=3)
    loan = Loan.objects.create(
        id='F14',
        member='reader',
        isbn='123',
        lent_on=due_on - timedelta(days=14),
    )

    response = client.get(f'/fees/{loan.id}')

    assert response.status_code == 200
    assert response.content.decode() == (
        f'<h1>Late fee for {loan.id}</h1><p>Due {due_on.isoformat()}, 3 day(s) late.</p>'
        '<p class="fee">Fee: $0.75</p>'
    )


@pytest.mark.django_db
def test_fee_page_uses_reading_room_layout_and_htmx_payment_action(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'Late fee \xc2\xb7 L3' in response.content
    assert b'Due' in response.content
    assert b'Dec 15, 2025' in response.content
    assert b'$4.75' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content
    assert b'hx-target="#payment-status"' in response.content


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('gateway_status', 'gateway_body', 'expected_status'),
    [
        (200, b'charged\n', 200),
        (503, b'declined\n', 502),
        (302, b'redirected\n', 502),
    ],
)
def test_payment_api_sends_the_characterized_request_and_maps_response(
    client, payment_gateway, gateway_status, gateway_body, expected_status
):
    payment_gateway.response_status = gateway_status
    payment_gateway.response_body = gateway_body

    response = client.post('/payments/L1')

    assert response.status_code == expected_status
    assert response['Content-Type'].startswith('text/plain')
    assert response.content == gateway_body
    assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_payment_api_does_not_call_gateway_for_an_unknown_loan(client, payment_gateway):
    response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response.content == b'no such loan\n'
    assert payment_gateway.requests == []


@pytest.mark.django_db
def test_payment_api_rejects_non_post_requests(client, payment_gateway):
    response = client.get('/payments/L1')

    assert response.status_code == 405
    assert payment_gateway.requests == []


@pytest.mark.django_db
def test_payment_api_maps_connection_failure_to_gateway_unavailable(client, payment_gateway):
    payment_gateway.shutdown()
    payment_gateway.server_close()

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'


@pytest.mark.django_db
def test_payment_api_turns_gateway_interruption_into_failure_without_losing_it(
    client, monkeypatch, caplog
):
    def interrupt(*args, **kwargs):
        raise InterruptedError('payment request interrupted')

    monkeypatch.setattr(urllib.request.OpenerDirector, 'open', interrupt)

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'
    assert 'payment request interrupted' in caplog.text
    assert any(
        isinstance(record.exc_info[1], InterruptedError)
        for record in caplog.records
        if record.exc_info
    )


@pytest.mark.django_db
def test_browser_shows_gateway_failure_after_htmx_payment(client, payment_gateway):
    payment_gateway.response_status = 503
    payment_gateway.response_body = b'declined\n'

    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="alert"' in response.content
    assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_browser_can_pay_a_fee_with_htmx(client, payment_gateway):
    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="status"' in response.content
    assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
@pytest.mark.usefixtures('restore_seed_loans')
def test_real_browser_can_view_and_pay_a_fee(live_server, payment_gateway):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/fees/L1/')
            assert page.get_by_role('heading', name='A little more time, a small fee.').is_visible()
            assert page.get_by_text('$10.00').is_visible()
            page.get_by_role('button', name='Pay late fee').click()

            if page.evaluate("typeof window.htmx !== 'undefined'"):
                page.get_by_role('status').wait_for()
                assert page.get_by_role('status').inner_text() == 'Payment received. Thank you.'
            else:
                page.wait_for_url('**/ui/fees/L1/')
        finally:
            browser.close()

    assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]
