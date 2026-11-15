from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest
from playwright.sync_api import sync_playwright

from src.loans.models import Loan


@pytest.fixture
def payment_gateway(monkeypatch):
    requests = []
    response = {'status': 200, 'body': b'charged\n'}

    class GatewayHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
            requests.append((self.command, self.path, body))
            self.send_response(response['status'])
            self.send_header('Content-Length', str(len(response['body'])))
            self.end_headers()
            self.wfile.write(response['body'])

        def log_message(self, format, *args):
            return

    server = ThreadingHTTPServer(('127.0.0.1', 0), GatewayHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', f'http://127.0.0.1:{server.server_port}')
    try:
        yield response, requests
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


@pytest.mark.django_db
def test_fee_endpoint_renders_the_characterized_amount_for_a_returned_loan(client):
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
    [
        (-1, '$0.00'),
        (0, '$0.00'),
        (1, '$0.00'),
        (2, '$0.00'),
        (3, '$0.75'),
        (40, '$10.00'),
    ],
)
def test_fee_endpoint_applies_grace_period_and_cap(client, days_late, expected_fee):
    due_on = date(2026, 1, 15)
    Loan.objects.create(
        id='F1',
        member='reader',
        isbn='123',
        lent_on=date(2026, 1, 1),
        returned_on=date.fromordinal(due_on.toordinal() + days_late),
    )

    response = client.get('/fees/F1')

    assert response.status_code == 200
    assert f'{max(days_late, 0)} day(s) late.'.encode() in response.content
    assert f'Fee: {expected_fee}'.encode() in response.content


@pytest.mark.django_db
def test_fee_endpoint_returns_the_characterized_not_found_response(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == '<p>No such loan.</p>'


@pytest.mark.django_db
def test_fee_page_shows_the_amount_and_htmx_payment_action(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'Fee note' in response.content
    assert b'19 day(s) late' in response.content
    assert b'$4.75' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content


@pytest.mark.django_db
def test_payment_endpoint_forwards_the_gateway_success(payment_gateway, client):
    response = client.post('/payments/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'charged\n'
    assert payment_gateway[1] == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_payment_endpoint_maps_non_200_gateway_responses_to_502(payment_gateway, client):
    payment_gateway[0].update(status=503, body=b'declined\n')

    response = client.post('/payments/L2')

    assert response.status_code == 502
    assert response.content == b'declined\n'
    assert payment_gateway[1] == [('POST', '/charge?loan=L2', b'')]


@pytest.mark.django_db
def test_payment_endpoint_does_not_call_gateway_for_an_unknown_loan(payment_gateway, client):
    response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'no such loan\n'
    assert payment_gateway[1] == []


@pytest.mark.django_db
def test_payment_endpoint_maps_gateway_connection_failures_to_502(client, monkeypatch):
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', 'http://127.0.0.1:1')

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'payment gateway unavailable\n'


@pytest.mark.django_db
def test_payment_endpoint_logs_an_interrupted_gateway_call(client, caplog, monkeypatch):
    from src.fees import gateway

    def interrupt(_request):
        raise InterruptedError('request interrupted')

    monkeypatch.setattr(gateway, 'urlopen', interrupt)

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'
    assert 'InterruptedError: request interrupted' in caplog.text


@pytest.mark.django_db
def test_fee_page_htmx_action_shows_gateway_success(payment_gateway, client):
    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="status"' in response.content
    assert b'charged' in response.content


@pytest.mark.django_db
def test_browser_can_view_and_pay_a_late_fee(payment_gateway, live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/fees/L3/')

            assert page.get_by_text('19 day(s) late.').is_visible()
            assert page.get_by_text('Late fee: $4.75').is_visible()
            page.get_by_role('button', name='Pay late fee').click()

            result = page.get_by_role('status')
            result.wait_for()
            assert result.inner_text() == 'charged'
        finally:
            browser.close()
    assert payment_gateway[1] == [('POST', '/charge?loan=L3', b'')]


@pytest.mark.parametrize(
    ('path', 'method'),
    [
        ('/fees/L3', 'post'),
        ('/payments/L1', 'get'),
        ('/ui/fees/L3/', 'post'),
        ('/ui/payments/L1/', 'get'),
    ],
)
@pytest.mark.django_db
def test_fee_and_payment_routes_reject_unsupported_methods(client, path, method):
    response = getattr(client, method)(path)

    assert response.status_code == 405
