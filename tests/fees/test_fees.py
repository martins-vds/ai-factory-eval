import json
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

import pytest
from playwright.sync_api import sync_playwright

from src.fees import gateway
from src.fees.gateway import PaymentGatewayError, charge_loan
from src.fees.services import calculate_late_fee
from src.loans.models import Loan

HTTP_GOLDEN_PATH = (
    Path(__file__).resolve().parents[2] / '.migration/characterization/source/goldens/http.json'
)
HTTP_GOLDENS = json.loads(HTTP_GOLDEN_PATH.read_text(encoding='utf-8'))
EDGE_GOLDEN_PATH = (
    Path(__file__).resolve().parents[2]
    / '.migration/characterization/source/goldens/edge-cases.json'
)
EDGE_GOLDENS = json.loads(EDGE_GOLDEN_PATH.read_text(encoding='utf-8'))


@pytest.fixture
def gateway_server(monkeypatch):
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = self.server.response_body
            request_body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
            self.server.requests.append((self.command, self.path, request_body))
            self.send_response(self.server.response_status)
            if self.server.response_status == 302:
                self.send_header('Location', '/redirect-target')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            body = b'redirected\n'
            self.server.requests.append((self.command, self.path, b''))
            self.send_response(200)
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            return

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    server.requests = []
    server.response_status = 200
    server.response_body = b'charged\n'
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setenv(
        'PAYMENT_GATEWAY_URL',
        f'http://127.0.0.1:{server.server_port}',
    )
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


@pytest.mark.django_db
def test_fee_api_matches_characterized_page(client):
    golden = HTTP_GOLDENS['GET /fees/{id}']

    response = client.get(golden['request']['path'])

    assert response.status_code == golden['response']['status']
    assert response['Content-Type'] == golden['response']['content_type']
    assert response.content.decode() == golden['response']['body']


@pytest.mark.django_db
def test_fee_api_formats_capped_amount_with_two_decimal_places(client):
    response = client.get('/fees/L1')

    assert response.status_code == 200
    assert b'Fee: $10.00' in response.content


@pytest.mark.parametrize(
    ('as_of', 'days_late', 'amount_cents'),
    [
        (date(2026, 1, 14), 0, 0),
        (date(2026, 1, 16), 1, 0),
        (date(2026, 1, 17), 2, 0),
        (date(2026, 1, 18), 3, 75),
        (date(2026, 3, 6), 50, 1000),
    ],
)
def test_fee_calculation_applies_grace_period_and_cap(as_of, days_late, amount_cents):
    loan = Loan(id='L9', member='reader', isbn='123', lent_on=date(2026, 1, 1))

    fee = calculate_late_fee(loan, as_of=as_of)

    assert fee.days_late == days_late
    assert fee.amount_cents == amount_cents


@pytest.mark.django_db
def test_fee_api_returns_characterized_not_found_for_unknown_loan(client):
    golden = EDGE_GOLDENS['GET /fees/unknown']['response']

    response = client.get('/fees/unknown')

    assert response.status_code == golden['status']
    assert response['Content-Type'] == golden['content_type']
    assert response.content.decode() == golden['body']


@pytest.mark.django_db
def test_fee_page_omits_payment_for_zero_balance(client):
    loan = Loan.objects.get(pk='L2')
    loan.returned_on = loan.due_on + date.resolution * 2
    loan.save(update_fields=['returned_on'])

    response = client.get('/ui/fees/L2/')

    assert response.status_code == 200
    assert b'Days late</dt><dd>2</dd>' in response.content
    assert b'Fee: $0.00' in response.content
    assert b'Pay late fee' not in response.content


@pytest.mark.django_db
def test_fee_page_shows_payment_for_three_days_late(client):
    loan = Loan.objects.get(pk='L2')
    loan.returned_on = loan.due_on + date.resolution * 3
    loan.save(update_fields=['returned_on'])

    response = client.get('/ui/fees/L2/')

    assert response.status_code == 200
    assert b'Days late</dt><dd>3</dd>' in response.content
    assert b'Fee: $0.75' in response.content
    assert b'hx-post="/ui/payments/L2/"' in response.content


@pytest.mark.django_db
def test_fee_page_returns_not_found_for_unknown_loan(client):
    response = client.get('/ui/fees/unknown/')

    assert response.status_code == 404
    assert response.content == b'<p>No such loan.</p>'


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('gateway_status', 'gateway_body', 'expected_status'),
    [
        (200, b'charged\n', 200),
        (503, b'declined\n', 502),
    ],
)
def test_payment_api_forwards_gateway_result(
    client, gateway_server, gateway_status, gateway_body, expected_status
):
    gateway_server.response_status = gateway_status
    gateway_server.response_body = gateway_body

    response = client.post('/payments/L1')

    assert response.status_code == expected_status
    assert response['Content-Type'] == 'text/plain'
    assert response.content == gateway_body
    assert gateway_server.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_payment_api_does_not_call_gateway_for_unknown_loan(client, gateway_server):
    golden = EDGE_GOLDENS['POST /payments/unknown']['response']

    response = client.post('/payments/unknown')

    assert response.status_code == golden['status']
    assert response['Content-Type'] == golden['content_type']
    assert response.content.decode() == golden['body']
    assert gateway_server.requests == []


@pytest.mark.django_db
def test_payment_api_does_not_follow_gateway_redirect(client, gateway_server):
    gateway_server.response_status = 302
    gateway_server.response_body = b'redirect body\n'

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'redirect body\n'
    assert gateway_server.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.parametrize(
    ('gateway_status', 'expected_status'),
    [(200, 200), (503, 502)],
)
@pytest.mark.django_db
def test_payment_api_replaces_invalid_utf8_from_gateway(
    client, gateway_server, gateway_status, expected_status
):
    gateway_server.response_status = gateway_status
    gateway_server.response_body = b'\xff'

    response = client.post('/payments/L1')

    assert response.status_code == expected_status
    assert response.content == '\ufffd'.encode()


@pytest.mark.parametrize(
    ('path', 'method'),
    [
        ('/fees/L3', 'post'),
        ('/ui/fees/L3/', 'post'),
        ('/payments/L1', 'get'),
        ('/ui/payments/L1/', 'get'),
    ],
)
@pytest.mark.django_db
def test_fee_and_payment_routes_reject_unsupported_methods(client, gateway_server, path, method):
    response = getattr(client, method)(path)

    assert response.status_code == 405
    assert gateway_server.requests == []


@pytest.mark.django_db
def test_payment_page_returns_not_found_for_unknown_loan(client, gateway_server):
    response = client.post('/ui/payments/unknown/', HTTP_HX_REQUEST='true')

    assert response.status_code == 404
    assert response.content == b'no such loan\n'
    assert gateway_server.requests == []


def test_payment_gateway_preserves_interrupted_call_as_cause(monkeypatch):
    class InterruptedOpener:
        def open(self, request):
            raise InterruptedError('cancelled')

    monkeypatch.setattr(gateway, 'build_opener', lambda *handlers: InterruptedOpener())

    with pytest.raises(PaymentGatewayError) as error:
        charge_loan('L1')

    assert isinstance(error.value.__cause__, InterruptedError)


@pytest.mark.django_db
def test_payment_api_surfaces_interrupted_call_as_gateway_failure(client, monkeypatch, caplog):
    class InterruptedOpener:
        def open(self, request):
            raise InterruptedError('cancelled')

    monkeypatch.setattr(gateway, 'build_opener', lambda *handlers: InterruptedOpener())

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'payment gateway unavailable\n'
    assert 'Payment gateway call interrupted' in caplog.text
    assert 'InterruptedError: cancelled' in caplog.text


@pytest.mark.django_db
def test_fee_page_shows_reading_room_content_and_htmx_payment_action(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'<!doctype html>' in response.content
    assert b'Late fee for L3' in response.content
    assert b'Fee: $4.75' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content


@pytest.mark.django_db
def test_htmx_payment_action_returns_success_status(client, gateway_server):
    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'<!doctype html>' not in response.content
    assert b'role="status"' in response.content
    assert b'Payment received for loan L1.' in response.content
    assert gateway_server.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_htmx_payment_action_surfaces_gateway_decline(client, gateway_server):
    gateway_server.response_status = 503
    gateway_server.response_body = b'declined\n'

    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 502
    assert response.content == b'declined\n'


@pytest.mark.django_db
def test_htmx_payment_action_surfaces_interruption(client, monkeypatch):
    class InterruptedOpener:
        def open(self, request):
            raise InterruptedError('cancelled')

    monkeypatch.setattr(gateway, 'build_opener', lambda *handlers: InterruptedOpener())

    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'


def test_payment_gateway_uses_the_source_default_url(monkeypatch):
    requests = []

    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, exception_type, exception, traceback):
            return False

        def read(self):
            return b'charged\n'

    class CapturingOpener:
        def open(self, request):
            requests.append((request.full_url, request.get_method(), request.data))
            return Response()

    monkeypatch.delenv('PAYMENT_GATEWAY_URL', raising=False)
    monkeypatch.setattr(gateway, 'build_opener', lambda *handlers: CapturingOpener())

    result = charge_loan('L1')

    assert result == (200, 'charged\n')
    assert requests == [('https://payments.lending-library.invalid/charge?loan=L1', 'POST', None)]


@pytest.mark.django_db
def test_real_browser_can_view_and_pay_late_fee(live_server, gateway_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/fees/L3/')
            assert page.get_by_role('heading', name='Late fee for L3').is_visible()
            htmx_available = page.evaluate("typeof window.htmx !== 'undefined'")

            page.get_by_role('button', name='Pay late fee').click()

            if htmx_available:
                page.get_by_role('status').wait_for()
                assert page.get_by_role('status').inner_text() == 'Payment received for loan L3.'
            else:
                page.wait_for_url('**/ui/fees/L3/')
                assert page.get_by_role('heading', name='Late fee for L3').is_visible()
            assert gateway_server.requests == [('POST', '/charge?loan=L3', b'')]
        finally:
            browser.close()
