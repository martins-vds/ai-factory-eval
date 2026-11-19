from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture
def payment_gateway(monkeypatch):
    class GatewayHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            self.server.requests.append(
                (self.command, self.path, self.rfile.read(int(self.headers['Content-Length'] or 0)))
            )
            self.send_response(self.server.response_status)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(self.server.response_body)

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), GatewayHandler)
    server.requests = []
    server.response_status = 200
    server.response_body = b'charged\n'
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', f'http://127.0.0.1:{server.server_port}')
    try:
        yield server
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


@pytest.mark.django_db
def test_fee_api_matches_the_characterized_html_response(client):
    response = client.get('/fees/L3')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == (
        '<h1>Late fee for L3</h1><p>Due 2025-12-15, 19 day(s) late.</p>'
        '<p class="fee">Fee: $4.75</p>'
    )


@pytest.mark.django_db
def test_fee_api_returns_the_characterized_unknown_loan_response(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content == b'<p>No such loan.</p>'


@pytest.mark.django_db
def test_fee_api_formats_a_capped_fee_as_two_decimal_dollars(client):
    response = client.get('/fees/L1')

    assert response.status_code == 200
    assert b'Fee: $10.00' in response.content


@pytest.mark.django_db
def test_fee_page_returns_not_found_for_an_unknown_loan(client):
    response = client.get('/ui/fees/unknown/')

    assert response.status_code == 404
    assert b'role="alert"' in response.content
    assert b'No such loan.' in response.content


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
def test_fee_and_payment_routes_reject_unsupported_methods(client, path, method):
    response = getattr(client, method)(path)

    assert response.status_code == 405


@pytest.mark.django_db
def test_fee_page_shows_fee_and_posts_payment_to_the_ui_route(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'Late fee for L3' in response.content
    assert b'19 day(s) late' in response.content
    assert b'Fee: $4.75' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content
    assert b'responseHandling' in response.content


@pytest.mark.django_db
def test_payment_api_forwards_the_gateway_request_and_success(payment_gateway, client):
    response = client.post('/payments/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'charged\n'
    assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_payment_api_maps_gateway_decline_to_502_and_preserves_body(payment_gateway, client):
    payment_gateway.response_status = 503
    payment_gateway.response_body = b'declined\n'

    response = client.post('/payments/L2')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'declined\n'
    assert payment_gateway.requests == [('POST', '/charge?loan=L2', b'')]


@pytest.mark.django_db
def test_payment_api_does_not_call_gateway_for_an_unknown_loan(payment_gateway, client):
    response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'no such loan\n'
    assert payment_gateway.requests == []


@pytest.mark.django_db
def test_payment_api_maps_connection_failure_to_gateway_unavailable(client, monkeypatch):
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', 'http://127.0.0.1:1')

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'payment gateway unavailable\n'


@pytest.mark.django_db
def test_htmx_payment_for_an_unknown_loan_returns_an_error_fragment(client):
    response = client.post('/ui/payments/unknown/', HTTP_HX_REQUEST='true')

    assert response.status_code == 404
    assert b'<!doctype html>' not in response.content
    assert b'role="alert"' in response.content
    assert b'No such loan.' in response.content


@pytest.mark.django_db
def test_htmx_payment_success_renders_a_status_fragment(payment_gateway, client):
    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'<!doctype html>' not in response.content
    assert b'role="status"' in response.content
    assert b'charged' in response.content
    assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_htmx_payment_failure_renders_an_error_fragment(payment_gateway, client):
    payment_gateway.response_status = 503
    payment_gateway.response_body = b'declined\n'

    response = client.post('/ui/payments/L2/', HTTP_HX_REQUEST='true')

    assert response.status_code == 502
    assert b'<!doctype html>' not in response.content
    assert b'role="alert"' in response.content
    assert b'declined' in response.content


@pytest.mark.django_db
def test_real_browser_can_pay_a_late_fee(payment_gateway, live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/fees/L1/')
            htmx_available = page.evaluate("typeof window.htmx !== 'undefined'")

            page.get_by_role('button', name='Pay late fee').click()

            if htmx_available:
                status = page.locator('#payment-status [role="status"]')
                status.wait_for()
            else:
                status = page.get_by_role('status')
                status.wait_for()
            assert 'Payment complete: charged' in status.inner_text()
            assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]
        finally:
            browser.close()


@pytest.mark.django_db
def test_real_browser_displays_payment_gateway_failures(payment_gateway, live_server):
    payment_gateway.response_status = 503
    payment_gateway.response_body = b'declined\n'

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/fees/L2/')
            htmx_available = page.evaluate("typeof window.htmx !== 'undefined'")

            page.get_by_role('button', name='Pay late fee').click()

            if htmx_available:
                alert = page.locator('#payment-status [role="alert"]')
                alert.wait_for()
            else:
                alert = page.get_by_role('alert')
                alert.wait_for()
            assert 'declined' in alert.inner_text()
            assert payment_gateway.requests == [('POST', '/charge?loan=L2', b'')]
        finally:
            browser.close()
