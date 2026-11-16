import urllib.request
from datetime import timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from typing import ClassVar

import pytest
from django.utils import timezone
from playwright.sync_api import sync_playwright

from src.fees.gateway import HttpPaymentGateway
from src.loans.models import Loan


@pytest.fixture
def payment_gateway(monkeypatch):
    class GatewayHandler(BaseHTTPRequestHandler):
        requests: ClassVar[list[tuple[str, str, bytes]]] = []
        status = 200
        response_body = b'charged\n'

        def do_POST(self):
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            self.requests.append((self.command, self.path, body))
            self.send_response(self.status)
            self.end_headers()
            self.wfile.write(self.response_body)

        def log_message(self, format, *args):
            pass

    GatewayHandler.requests = []
    server = ThreadingHTTPServer(('127.0.0.1', 0), GatewayHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setenv(
        'PAYMENT_GATEWAY_URL',
        f'http://127.0.0.1:{server.server_port}',
    )
    try:
        yield GatewayHandler
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


def test_payment_gateway_does_not_override_the_default_timeout(monkeypatch):
    class GatewayResponse:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return None

        def read(self):
            return b'charged\n'

    urlopen_options = {}

    def urlopen(request, **options):
        urlopen_options.update(options)
        return GatewayResponse()

    monkeypatch.setattr(urllib.request, 'urlopen', urlopen)

    response = HttpPaymentGateway().charge('L1')

    assert response.status_code == 200
    assert response.body == b'charged\n'
    assert urlopen_options == {}


@pytest.mark.django_db
def test_fee_api_renders_the_characterized_late_fee(client):
    response = client.get('/fees/L3')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == (
        '<h1>Late fee for L3</h1><p>Due 2025-12-15, 19 day(s) late.</p>'
        '<p class="fee">Fee: $4.75</p>'
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('days_late', 'expected_fee'),
    [(0, '$0.00'), (1, '$0.00'), (2, '$0.00'), (3, '$0.75'), (50, '$10.00')],
)
def test_fee_api_applies_waiver_rate_and_cap(client, days_late, expected_fee):
    today = timezone.localdate()
    loan = Loan.objects.create(
        id=f'boundary-{days_late}',
        member='reader',
        isbn='123',
        lent_on=today - timedelta(days=14 + days_late),
    )

    response = client.get(f'/fees/{loan.id}')

    assert response.status_code == 200
    assert f'{days_late} day(s) late.'.encode() in response.content
    assert f'Fee: {expected_fee}'.encode() in response.content


@pytest.mark.django_db
def test_fee_api_returns_the_characterized_not_found_fragment(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content == b'<p>No such loan.</p>'


@pytest.mark.django_db
def test_fee_page_uses_reading_room_layout_and_htmx_payment_action(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'Late fee for L3' in response.content
    assert b'Due Dec 15, 2025' in response.content
    assert b'19 day(s) late' in response.content
    assert b'Fee: $4.75' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content
    assert b'htmx.org@2.0.11' in response.content
    assert b'daisyui@4.12.24' in response.content


@pytest.mark.django_db
def test_ui_routes_return_not_found_for_unknown_loans(client, payment_gateway):
    fee_response = client.get('/ui/fees/unknown/')
    payment_response = client.post('/ui/payments/unknown/')

    assert fee_response.status_code == 404
    assert fee_response['Content-Type'] == 'text/html'
    assert fee_response.content == b'<p>No such loan.</p>'
    assert payment_response.status_code == 404
    assert payment_response['Content-Type'] == 'text/html'
    assert payment_response.content == b'<p>No such loan.</p>'
    assert payment_gateway.requests == []


@pytest.mark.django_db
def test_fee_and_payment_routes_restrict_http_methods(client, payment_gateway):
    responses = [
        client.post('/fees/L3'),
        client.put('/payments/L1'),
        client.post('/ui/fees/L3/'),
        client.get('/ui/payments/L1/'),
    ]

    assert [response.status_code for response in responses] == [405, 405, 405, 405]
    assert payment_gateway.requests == []


@pytest.mark.django_db
def test_payment_api_forwards_the_charge_request(client, payment_gateway):
    response = client.post('/payments/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'charged\n'
    assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_payment_api_maps_gateway_errors_and_preserves_response_body(client, payment_gateway):
    payment_gateway.status = 503
    payment_gateway.response_body = b'declined\n'

    response = client.post('/payments/L2')

    assert response.status_code == 502
    assert response.content == b'declined\n'
    assert payment_gateway.requests == [('POST', '/charge?loan=L2', b'')]


@pytest.mark.django_db
def test_payment_api_does_not_call_gateway_for_an_unknown_loan(client, payment_gateway):
    response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'no such loan\n'
    assert payment_gateway.requests == []


@pytest.mark.django_db
def test_payment_api_maps_connection_errors_to_gateway_unavailable(client, monkeypatch):
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', 'http://127.0.0.1:1')

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'


@pytest.mark.django_db
def test_payment_api_logs_interruption_and_returns_gateway_failure(client, monkeypatch, caplog):
    def interrupt(*args, **kwargs):
        raise InterruptedError('gateway request interrupted')

    monkeypatch.setattr(urllib.request, 'urlopen', interrupt)

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'
    assert 'InterruptedError: gateway request interrupted' in caplog.text


@pytest.mark.django_db
def test_browser_payment_action_swaps_a_success_status(client, payment_gateway):
    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'<!doctype html>' not in response.content
    assert b'role="status"' in response.content
    assert b'charged' in response.content
    assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_browser_payment_action_swaps_a_gateway_error(client, payment_gateway):
    payment_gateway.status = 503
    payment_gateway.response_body = b'declined\n'

    response = client.post('/ui/payments/L2/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="alert"' in response.content
    assert b'declined' in response.content


@pytest.mark.django_db
def test_browser_payment_form_redirects_after_successful_charge(client, payment_gateway):
    response = client.post('/ui/payments/L1/')

    assert response.status_code == 302
    assert response['Location'] == '/ui/fees/L1/'
    assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_regular_browser_payment_failure_renders_safe_gateway_message(client, payment_gateway):
    payment_gateway.status = 503
    payment_gateway.response_body = b'<script>declined\xff</script>\n'

    response = client.post('/ui/payments/L2/')

    assert response.status_code == 200
    assert b'Late fee for L2' in response.content
    assert b'Fee: $0.00' in response.content
    assert b'role="alert"' in response.content
    assert b'&lt;script&gt;declined\xef\xbf\xbd&lt;/script&gt;' in response.content
    assert b'<script>' not in response.content


@pytest.mark.django_db
def test_real_browser_can_view_and_pay_a_late_fee(live_server, payment_gateway):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/fees/L3/')
            assert page.get_by_role('heading', name='Late fee for L3').is_visible()
            assert page.get_by_text('Fee: $4.75').is_visible()

            htmx_available = page.evaluate("typeof window.htmx !== 'undefined'")
            page.get_by_role('button', name='Pay late fee').click()
            if htmx_available:
                page.get_by_role('status').wait_for()
                assert page.get_by_role('status').inner_text() == 'Payment received: charged'
            else:
                page.wait_for_url('**/ui/fees/L3/')

            assert payment_gateway.requests == [('POST', '/charge?loan=L3', b'')]
        finally:
            browser.close()
