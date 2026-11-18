from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from typing import ClassVar

import pytest


@pytest.fixture
def payment_gateway(monkeypatch):
    class GatewayHandler(BaseHTTPRequestHandler):
        requests: ClassVar[list[tuple[str, str, bytes]]] = []
        status = 200
        body = b'charged\n'
        location = None

        def do_POST(self):
            self.requests.append(
                (self.command, self.path, self.rfile.read(int(self.headers['Content-Length'] or 0)))
            )
            self.respond()

        def do_GET(self):
            self.requests.append((self.command, self.path, b''))
            self.respond()

        def respond(self):
            self.send_response(self.status)
            if self.location:
                self.send_header('Location', self.location)
            self.end_headers()
            self.wfile.write(self.body)

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), GatewayHandler)
    thread = Thread(target=server.serve_forever)
    thread.start()
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', f'http://127.0.0.1:{server.server_port}')
    try:
        yield GatewayHandler
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


@pytest.mark.django_db
def test_fee_api_matches_the_characterized_html(client):
    response = client.get('/fees/L3')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == (
        '<h1>Late fee for L3</h1><p>Due 2025-12-15, 19 day(s) late.</p>'
        '<p class="fee">Fee: $4.75</p>'
    )


@pytest.mark.django_db
def test_fee_api_returns_the_characterized_not_found_response(client):
    response = client.get('/fees/missing')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == '<p>No such loan.</p>'


@pytest.mark.django_db
def test_fee_page_uses_reading_room_layout_and_posts_to_ui_payment_path(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'A small nudge, never a surprise' in response.content
    assert b'19 late days' in response.content
    assert b'Fee: $4.75' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content
    assert b'htmx:beforeSwap' in response.content


@pytest.mark.django_db
def test_payment_api_posts_to_gateway_and_forwards_success(client, payment_gateway):
    response = client.post('/payments/L3')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'charged\n'
    assert payment_gateway.requests == [('POST', '/charge?loan=L3', b'')]


@pytest.mark.django_db
def test_payment_api_maps_gateway_failure_to_502_and_forwards_body(client, payment_gateway):
    payment_gateway.status = 503
    payment_gateway.body = b'declined\n'

    response = client.post('/payments/L3')

    assert response.status_code == 502
    assert response.content == b'declined\n'
    assert payment_gateway.requests == [('POST', '/charge?loan=L3', b'')]


@pytest.mark.django_db
def test_payment_api_does_not_follow_gateway_redirects(client, payment_gateway):
    payment_gateway.status = 302
    payment_gateway.body = b'redirected\n'
    payment_gateway.location = '/redirected'

    response = client.post('/payments/L3')

    assert response.status_code == 502
    assert response.content == b'redirected\n'
    assert payment_gateway.requests == [('POST', '/charge?loan=L3', b'')]


@pytest.mark.django_db
def test_unknown_payment_does_not_call_gateway(client, payment_gateway):
    response = client.post('/payments/missing')

    assert response.status_code == 404
    assert response.content == b'no such loan\n'
    assert payment_gateway.requests == []


@pytest.mark.django_db
def test_payment_api_surfaces_interrupted_gateway_call_as_502(client, monkeypatch):
    def interrupt(request):
        raise InterruptedError('request interrupted')

    class Opener:
        def open(self, request):
            return interrupt(request)

    monkeypatch.setattr('src.fees.gateway.build_opener', lambda *handlers: Opener())

    response = client.post('/payments/L3')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'


@pytest.mark.django_db
def test_payment_api_maps_io_failure_to_gateway_unavailable(client, monkeypatch):
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', 'http://127.0.0.1:1')

    response = client.post('/payments/L3')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'


@pytest.mark.django_db
def test_htmx_payment_failure_renders_an_error_fragment(client, payment_gateway):
    payment_gateway.status = 503
    payment_gateway.body = b'declined\n'

    response = client.post('/ui/payments/L3/', HTTP_HX_REQUEST='true')

    assert response.status_code == 502
    assert b'role="alert"' in response.content
    assert b'declined' in response.content


@pytest.mark.django_db
def test_unknown_fee_page_renders_not_found(client):
    response = client.get('/ui/fees/missing/')

    assert response.status_code == 404
    assert b'role="alert"' in response.content


@pytest.mark.django_db
def test_unknown_ui_payment_renders_error_fragment(client):
    response = client.post('/ui/payments/missing/', HTTP_HX_REQUEST='true')

    assert response.status_code == 404
    assert b'role="alert"' in response.content


@pytest.mark.django_db
def test_payment_page_can_pay_from_browser(client, payment_gateway):
    response = client.post('/ui/payments/L3/')

    assert response.status_code == 200
    assert b'role="status"' in response.content
    assert b'charged' in response.content
    assert payment_gateway.requests == [('POST', '/charge?loan=L3', b'')]


@pytest.mark.django_db
def test_browser_can_pay_from_fee_page(live_server, payment_gateway):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/fees/L3/')
            assert page.get_by_role('heading', name='Late fees').is_visible()
            page.get_by_role('button', name='Pay late fee').click()
            result = page.locator('#payment-result [role="status"]')
            result.wait_for()
            assert 'charged' in result.inner_text()
        finally:
            browser.close()
