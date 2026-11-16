import threading
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import URLError

import pytest
from django.utils import timezone
from playwright.sync_api import sync_playwright

from src.loans.models import Loan


@pytest.fixture
def payment_gateway():
    class GatewayHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = self.rfile.read(int(self.headers.get('Content-Length', 0))).decode()
            self.server.requests.append((self.command, self.path, body))
            self.send_response(self.server.response_status)
            self.send_header('Content-Type', 'text/plain')
            for name, value in getattr(self.server, 'response_headers', []):
                self.send_header(name, value)
            self.end_headers()
            self.wfile.write(self.server.response_body.encode())

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), GatewayHandler)
    server.requests = []
    server.response_status = 200
    server.response_body = 'charged\n'
    server.response_headers = []
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}', server
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


@pytest.mark.django_db
def test_payment_api_posts_to_the_gateway_and_forwards_success(
    client, monkeypatch, payment_gateway
):
    loan = Loan.objects.create(id='F1', member='reader', isbn='123', lent_on=date(2026, 1, 1))
    gateway_url, gateway = payment_gateway
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

    response = client.post(f'/payments/{loan.id}')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'charged\n'
    assert gateway.requests == [('POST', '/charge?loan=F1', '')]


@pytest.mark.django_db
def test_payment_api_maps_gateway_failure_to_bad_gateway(client, monkeypatch, payment_gateway):
    loan = Loan.objects.create(id='F1', member='reader', isbn='123', lent_on=date(2026, 1, 1))
    gateway_url, gateway = payment_gateway
    gateway.response_status = 503
    gateway.response_body = 'declined\n'
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

    response = client.post(f'/payments/{loan.id}')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'declined\n'
    assert gateway.requests == [('POST', '/charge?loan=F1', '')]


@pytest.mark.django_db
def test_payment_api_maps_successful_non_200_response_to_bad_gateway(
    client, monkeypatch, payment_gateway
):
    loan = Loan.objects.create(id='F1', member='reader', isbn='123', lent_on=date(2026, 1, 1))
    gateway_url, gateway = payment_gateway
    gateway.response_status = 201
    gateway.response_body = 'accepted\n'
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

    response = client.post(f'/payments/{loan.id}')

    assert response.status_code == 502
    assert response.content.decode() == 'accepted\n'


@pytest.mark.django_db
def test_payment_api_does_not_follow_gateway_redirects(client, monkeypatch, payment_gateway):
    loan = Loan.objects.create(id='F1', member='reader', isbn='123', lent_on=date(2026, 1, 1))
    gateway_url, gateway = payment_gateway
    gateway.response_status = 302
    gateway.response_body = 'redirected\n'
    gateway.response_headers = [('Location', f'{gateway_url}/redirect')]
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

    response = client.post(f'/payments/{loan.id}')

    assert response.status_code == 502
    assert response.content.decode() == 'redirected\n'
    assert gateway.requests == [('POST', '/charge?loan=F1', '')]


@pytest.mark.django_db
def test_payment_api_does_not_call_gateway_for_an_unknown_loan(
    client, monkeypatch, payment_gateway
):
    gateway_url, gateway = payment_gateway
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

    response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'
    assert gateway.requests == []


@pytest.mark.django_db
def test_ui_payment_does_not_call_gateway_for_an_unknown_loan(client, monkeypatch, payment_gateway):
    gateway_url, gateway = payment_gateway
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

    response = client.post('/ui/payments/unknown/', HTTP_HX_REQUEST='true')

    assert response.status_code == 404
    assert response.content.decode() == '<p>No such loan.</p>'
    assert gateway.requests == []


@pytest.mark.django_db
def test_payment_api_rejects_non_post_methods(client, monkeypatch, payment_gateway):
    loan = Loan.objects.create(id='F1', member='reader', isbn='123', lent_on=date(2026, 1, 1))
    gateway_url, gateway = payment_gateway
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

    response = client.get(f'/payments/{loan.id}')

    assert response.status_code == 405
    assert gateway.requests == []


@pytest.mark.django_db
def test_htmx_payment_uses_the_ui_path_and_returns_a_status_fragment(
    client, monkeypatch, payment_gateway
):
    loan = Loan.objects.create(id='F1', member='reader', isbn='123', lent_on=date(2026, 1, 1))
    gateway_url, gateway = payment_gateway
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

    response = client.post(f'/ui/payments/{loan.id}/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="status"' in response.content
    assert b'Payment complete' in response.content
    assert b'<!doctype html>' not in response.content
    assert gateway.requests == [('POST', '/charge?loan=F1', '')]


@pytest.mark.django_db
def test_htmx_payment_shows_gateway_failure(client, monkeypatch, payment_gateway):
    loan = Loan.objects.create(id='F1', member='reader', isbn='123', lent_on=date(2026, 1, 1))
    gateway_url, gateway = payment_gateway
    gateway.response_status = 503
    gateway.response_body = 'declined\n'
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

    response = client.post(f'/ui/payments/{loan.id}/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="alert"' in response.content
    assert b'Payment could not be completed. declined' in response.content


@pytest.mark.django_db
def test_regular_fee_payment_renders_a_full_page_result(client, monkeypatch, payment_gateway):
    loan = Loan.objects.create(id='F1', member='reader', isbn='123', lent_on=date(2026, 1, 1))
    gateway_url, gateway = payment_gateway
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

    response = client.post(f'/ui/payments/{loan.id}/')

    assert response.status_code == 200
    assert b'<!doctype html>' in response.content
    assert b'role="status"' in response.content
    assert b'Payment complete' in response.content
    assert gateway.requests == [('POST', '/charge?loan=F1', '')]


@pytest.mark.django_db
def test_payment_api_returns_gateway_failure_when_connection_fails(client, monkeypatch):
    loan = Loan.objects.create(id='F1', member='reader', isbn='123', lent_on=date(2026, 1, 1))
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', 'http://127.0.0.1:1')

    response = client.post(f'/payments/{loan.id}')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'payment gateway unavailable\n'


@pytest.mark.django_db
def test_payment_api_returns_gateway_failure_for_an_os_error(client, monkeypatch):
    loan = Loan.objects.create(id='F1', member='reader', isbn='123', lent_on=date(2026, 1, 1))

    class FailedOpener:
        def open(self, outbound_request):
            raise OSError('socket failed')

    monkeypatch.setattr(
        'src.fees.gateway.request.build_opener',
        lambda *handlers: FailedOpener(),
    )

    response = client.post(f'/payments/{loan.id}')

    assert response.status_code == 502
    assert response.content.decode() == 'payment gateway unavailable\n'


@pytest.mark.django_db
@pytest.mark.parametrize('wrapped', [False, True])
def test_payment_api_logs_and_maps_interrupted_gateway_calls(client, monkeypatch, caplog, wrapped):
    loan = Loan.objects.create(id='F1', member='reader', isbn='123', lent_on=date(2026, 1, 1))
    requested_urls = []
    monkeypatch.delenv('PAYMENT_GATEWAY_URL', raising=False)

    class InterruptedOpener:
        def open(self, outbound_request):
            requested_urls.append(outbound_request.full_url)
            error = InterruptedError('request interrupted')
            if wrapped:
                raise URLError(error)
            raise error

    monkeypatch.setattr(
        'src.fees.gateway.request.build_opener',
        lambda *handlers: InterruptedOpener(),
    )

    response = client.post(f'/payments/{loan.id}')

    assert response.status_code == 502
    assert response.content.decode() == 'payment gateway unavailable\n'
    assert any(
        record.getMessage() == 'Payment gateway request interrupted' for record in caplog.records
    )
    assert 'InterruptedError: request interrupted' in caplog.text
    assert requested_urls == ['https://payments.lending-library.invalid/charge?loan=F1']


@pytest.mark.django_db
def test_real_browser_can_view_and_pay_a_late_fee(live_server, monkeypatch, payment_gateway):
    today = timezone.localdate()
    loan = Loan.objects.create(
        id='F1',
        member='reader',
        isbn='123',
        lent_on=today - timedelta(days=17),
    )
    gateway_url, gateway = payment_gateway
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/fees/{loan.id}/')

            assert page.get_by_role('heading', name='Late fees').is_visible()
            assert page.get_by_text('$0.75', exact=True).is_visible()

            htmx_available = page.evaluate("typeof window.htmx !== 'undefined'")
            page.get_by_role('button', name='Pay $0.75').click()
            page.get_by_role('status').wait_for()

            assert 'Payment complete' in page.get_by_role('status').inner_text()
            assert page.get_by_role('heading', name='Late fees').is_visible()
            if not htmx_available:
                assert page.get_by_text('Payment complete').is_visible()
        finally:
            browser.close()

    assert gateway.requests == [('POST', '/charge?loan=F1', '')]
