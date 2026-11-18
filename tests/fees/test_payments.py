from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from unittest.mock import Mock

import pytest
from playwright.sync_api import sync_playwright

from src.fees.gateway import DEFAULT_PAYMENT_GATEWAY_URL, HttpPaymentGateway
from src.fees.services import GatewayResponse, PaymentApplication


@pytest.fixture
def payment_gateway(monkeypatch):
    state = {'request': None, 'status': 200, 'body': b'charged\n'}

    class GatewayHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get('Content-Length', 0))
            state['request'] = (self.command, self.path, self.rfile.read(length))
            self.send_response(state['status'])
            self.send_header('Content-Length', str(len(state['body'])))
            self.end_headers()
            self.wfile.write(state['body'])

        def log_message(self, format, *args):
            return

    server = ThreadingHTTPServer(('127.0.0.1', 0), GatewayHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setenv(
        'PAYMENT_GATEWAY_URL',
        f'http://127.0.0.1:{server.server_address[1]}',
    )
    try:
        yield state
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


@pytest.mark.django_db
def test_payment_endpoint_sends_characterized_request_and_forwards_success(client, payment_gateway):
    response = client.post('/payments/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'charged\n'
    assert payment_gateway['request'] == ('POST', '/charge?loan=L1', b'')


def test_payment_application_sends_characterized_request_to_gateway(payment_gateway):
    repository = Mock()
    repository.find.return_value = object()

    result = PaymentApplication(repository, HttpPaymentGateway()).charge('L1')

    assert result.status == 200
    assert result.body == 'charged\n'
    assert payment_gateway['request'] == ('POST', '/charge?loan=L1', b'')


def test_payment_application_does_not_call_gateway_for_unknown_loan():
    repository = Mock()
    repository.find.return_value = None
    gateway = Mock()

    result = PaymentApplication(repository, gateway).charge('unknown')

    assert result.status == 404
    assert result.body == 'no such loan\n'
    gateway.charge.assert_not_called()


@pytest.mark.parametrize(
    ('gateway_status', 'expected_status'),
    [(200, 200), (503, 502)],
)
def test_payment_application_maps_gateway_status_and_preserves_body(
    gateway_status, expected_status
):
    repository = Mock()
    repository.find.return_value = object()
    gateway = Mock()
    gateway.charge.return_value = GatewayResponse(gateway_status, 'gateway body\n')

    result = PaymentApplication(repository, gateway).charge('L1')

    assert result.status == expected_status
    assert result.body == 'gateway body\n'
    gateway.charge.assert_called_once_with('L1')


@pytest.mark.django_db
def test_payment_endpoint_maps_gateway_failure_to_502_and_preserves_body(client, payment_gateway):
    payment_gateway['status'] = 503
    payment_gateway['body'] = b'declined\n'

    response = client.post('/payments/L2')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'declined\n'
    assert payment_gateway['request'] == ('POST', '/charge?loan=L2', b'')


@pytest.mark.django_db
def test_payment_endpoint_does_not_call_gateway_for_unknown_loan(client, payment_gateway):
    response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response.content.decode() == 'no such loan\n'
    assert payment_gateway['request'] is None


@pytest.mark.django_db
def test_payment_endpoint_maps_connection_failure_to_characterized_502(client, monkeypatch):
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', 'http://127.0.0.1:1')

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content.decode() == 'payment gateway unavailable\n'


def test_payment_application_retains_interrupted_gateway_error():
    interruption = InterruptedError('request interrupted')

    class LoanRepository:
        def find(self, loan_id):
            return object()

    class InterruptedGateway:
        def charge(self, loan_id):
            raise interruption

    result = PaymentApplication(LoanRepository(), InterruptedGateway()).charge('L1')

    assert result.status == 502
    assert result.body == 'payment gateway unavailable\n'
    assert result.failure is interruption


def test_payment_application_maps_io_failure_to_gateway_unavailable():
    failure = OSError('connection failed')
    repository = Mock()
    repository.find.return_value = object()
    gateway = Mock()
    gateway.charge.side_effect = failure

    result = PaymentApplication(repository, gateway).charge('L1')

    assert result.status == 502
    assert result.body == 'payment gateway unavailable\n'
    assert result.failure is failure


def test_payment_gateway_uses_characterized_default_url():
    assert DEFAULT_PAYMENT_GATEWAY_URL == 'https://payments.lending-library.invalid'


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('path', 'method'),
    [
        ('/fees/L1', 'post'),
        ('/ui/fees/L1/', 'post'),
        ('/payments/L1', 'get'),
        ('/ui/payments/L1/', 'get'),
    ],
)
def test_fee_and_payment_routes_reject_unsupported_methods(client, payment_gateway, path, method):
    response = getattr(client, method)(path)

    assert response.status_code == 405
    assert payment_gateway['request'] is None


@pytest.mark.django_db
def test_htmx_payment_action_renders_success_fragment(client, payment_gateway):
    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'<!doctype html>' not in response.content
    assert b'id="payment-status"' in response.content
    assert b'role="status"' in response.content
    assert b'charged' in response.content


@pytest.mark.django_db
def test_htmx_payment_action_renders_gateway_failure_safely(client, payment_gateway):
    payment_gateway['status'] = 503
    payment_gateway['body'] = b'<b>declined</b>\n'

    response = client.post('/ui/payments/L2/', HTTP_HX_REQUEST='true')

    assert response.status_code == 502
    assert b'<!doctype html>' not in response.content
    assert b'role="alert"' in response.content
    assert b'&lt;b&gt;declined&lt;/b&gt;' in response.content
    assert b'<b>declined</b>' not in response.content


@pytest.mark.django_db
def test_regular_payment_action_renders_a_complete_result_page(client, payment_gateway):
    response = client.post('/ui/payments/L1/')

    assert response.status_code == 200
    assert b'<!doctype html>' in response.content
    assert b'Payment result</h1>' in response.content
    assert b'href="/ui/fees/L1/"' in response.content
    assert b'role="status"' in response.content
    assert b'charged' in response.content


@pytest.mark.django_db
def test_browser_can_pay_from_the_fee_page(payment_gateway, live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/fees/L1/')
            assert page.get_by_role('heading', name='Late fee for L1').is_visible()
            htmx_available = page.evaluate("typeof window.htmx !== 'undefined'")

            page.get_by_role('button', name='Pay late fee').click()

            if htmx_available:
                page.get_by_role('status').wait_for()
                assert page.get_by_role('status').inner_text() == 'charged'
            else:
                page.wait_for_url('**/ui/payments/L1/')
                assert page.get_by_role('status').inner_text() == 'charged'
        finally:
            browser.close()


@pytest.mark.django_db
def test_browser_displays_gateway_failure_from_htmx_payment_action(payment_gateway, live_server):
    payment_gateway['status'] = 503
    payment_gateway['body'] = b'declined\n'

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/fees/L1/')

            page.get_by_role('button', name='Pay late fee').click()

            alert = page.get_by_role('alert')
            alert.wait_for()
            assert alert.inner_text() == 'declined'
        finally:
            browser.close()
