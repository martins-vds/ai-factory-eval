import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import URLError

import pytest
from playwright.sync_api import sync_playwright

from src.fees.gateway import HttpPaymentGateway
from src.fees.services import GatewayResponse, InterruptedPayment


@pytest.fixture
def payment_gateway(monkeypatch):
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            self.server.requests.append((self.command, self.path, body))
            status, response_body = {
                '/charge?loan=L2': (503, b'declined\n'),
                '/charge?loan=L3': (302, b'redirected\n'),
                '/charge?loan=L4': (200, b'\xff\n'),
                '/charge?loan=L5': (503, b'\xff\n'),
            }.get(self.path, (200, b'charged\n'))
            self.send_response(status)
            if status == 302:
                self.send_header('Location', '/redirected')
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', str(len(response_body)))
            self.end_headers()
            self.wfile.write(response_body)

        def log_message(self, _format, *_args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    server.requests = []
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    monkeypatch.setenv(
        'PAYMENT_GATEWAY_URL',
        f'http://127.0.0.1:{server.server_port}',
    )
    try:
        yield server
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


@pytest.mark.django_db
def test_fee_api_matches_characterized_fragment(client):
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
    assert response.content.decode() == '<p>No such loan.</p>'


@pytest.mark.django_db
def test_fee_api_formats_a_capped_fee_as_two_decimal_places(client):
    response = client.get('/fees/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html'
    assert 'Fee: $10.00</p>' in response.content.decode()


@pytest.mark.parametrize('path', ['/fees/L3', '/ui/fees/L3/'])
@pytest.mark.django_db
def test_fee_endpoints_only_accept_get(client, path):
    assert client.post(path).status_code == 405


@pytest.mark.parametrize('path', ['/payments/L1', '/ui/payments/L1/'])
@pytest.mark.django_db
def test_payment_endpoints_only_accept_post(client, path):
    assert client.get(path).status_code == 405


@pytest.mark.django_db
def test_fee_page_offers_htmx_payment_and_swaps_error_responses(client):
    response = client.get('/ui/fees/L3/')
    body = response.content.decode()

    assert response.status_code == 200
    assert 'Late fee for L3' in body
    assert 'Fee: $4.75' in body
    assert 'hx-post="/ui/payments/L3/"' in body
    assert 'hx-on::before-swap=' in body


@pytest.mark.django_db
def test_fee_page_returns_not_found_for_unknown_loan(client):
    response = client.get('/ui/fees/unknown/')

    assert response.status_code == 404
    assert 'No such loan.' in response.content.decode()


@pytest.mark.django_db
def test_fee_page_renders_in_a_browser(live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            response = page.goto(f'{live_server.url}/ui/fees/L3/')
            assert response is not None
            assert response.status == 200
            assert page.get_by_role('heading', name='Late fee for L3').is_visible()
            assert page.get_by_text('Fee: $4.75').is_visible()
            assert page.get_by_role('button', name='Pay late fee').is_visible()
        finally:
            browser.close()


@pytest.mark.django_db
def test_payment_api_forwards_gateway_request_and_maps_responses(client, payment_gateway):
    success = client.post('/payments/L1')
    failure = client.post('/payments/L2')

    assert (success.status_code, success['Content-Type'], success.content.decode()) == (
        200,
        'text/plain',
        'charged\n',
    )
    assert (failure.status_code, failure['Content-Type'], failure.content.decode()) == (
        502,
        'text/plain',
        'declined\n',
    )
    assert payment_gateway.requests == [
        ('POST', '/charge?loan=L1', b''),
        ('POST', '/charge?loan=L2', b''),
    ]


@pytest.mark.django_db
def test_payment_api_maps_redirects_to_bad_gateway_without_following_them(client, payment_gateway):
    response = client.post('/payments/L3')

    assert (response.status_code, response.content.decode()) == (502, 'redirected\n')
    assert payment_gateway.requests == [('POST', '/charge?loan=L3', b'')]


@pytest.mark.django_db
def test_payment_api_does_not_call_gateway_for_unknown_loan(client, payment_gateway):
    response = client.post('/payments/unknown')

    assert (response.status_code, response.content.decode()) == (404, 'no such loan\n')
    assert response['Content-Type'] == 'text/plain'
    assert payment_gateway.requests == []


def test_http_gateway_preserves_non_success_status_and_body(payment_gateway):
    response = HttpPaymentGateway().charge('L2')

    assert response == GatewayResponse(503, 'declined\n')
    assert payment_gateway.requests == [('POST', '/charge?loan=L2', b'')]


def test_http_gateway_replaces_invalid_utf8_in_response_body(payment_gateway):
    response = HttpPaymentGateway().charge('L4')

    assert response == GatewayResponse(200, '\ufffd\n')


def test_http_gateway_replaces_invalid_utf8_in_error_body(payment_gateway):
    response = HttpPaymentGateway().charge('L5')

    assert response == GatewayResponse(503, '\ufffd\n')


@pytest.mark.django_db
def test_payment_page_swaps_gateway_error_fragment(client, payment_gateway):
    response = client.post(
        '/ui/payments/L2/',
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 502
    assert response['Content-Type'].startswith('text/html')
    assert 'Payment could not be completed' in response.content.decode()
    assert 'declined' in response.content.decode()
    assert 'hx-on::before-swap=' in response.content.decode()
    assert 'Try payment again' in response.content.decode()


@pytest.mark.django_db
def test_payment_page_swaps_success_fragment(client, payment_gateway):
    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert 'Payment accepted.' in response.content.decode()
    assert 'charged' in response.content.decode()


@pytest.mark.django_db
def test_payment_page_returns_fragment_for_unknown_loan(client, payment_gateway):
    response = client.post('/ui/payments/unknown/', HTTP_HX_REQUEST='true')

    assert response.status_code == 404
    assert 'No such loan.' in response.content.decode()
    assert 'Try payment again' in response.content.decode()
    assert 'hx-post="/ui/payments/unknown/"' in response.content.decode()


@pytest.mark.django_db
def test_payment_page_renders_gateway_failure_without_htmx(client, monkeypatch):
    class FailedOpener:
        def open(self, _request):
            raise OSError('connection unavailable')

    monkeypatch.setattr(
        'urllib.request.build_opener',
        lambda *_handlers: FailedOpener(),
    )
    response = client.post('/ui/payments/L1/')

    assert response.status_code == 502
    assert 'Payment could not be completed: payment gateway unavailable' in (
        response.content.decode()
    )
    assert 'Fee: $10.00' in response.content.decode()


@pytest.mark.django_db
def test_payment_page_renders_gateway_response_without_htmx(client, payment_gateway):
    response = client.post('/ui/payments/L2/')

    assert response.status_code == 502
    assert 'Late fee for L2' in response.content.decode()
    assert 'Fee: $0.00' in response.content.decode()
    assert 'Payment could not be completed: declined' in response.content.decode()


@pytest.mark.django_db
def test_regular_payment_page_redirects_to_fee_page(client, payment_gateway):
    response = client.post('/ui/payments/L1/')

    assert response.status_code == 302
    assert response['Location'] == '/ui/fees/L1/'


@pytest.mark.django_db
def test_interrupted_payment_is_a_gateway_failure_without_losing_interrupt(client, monkeypatch):
    class InterruptedOpener:
        def open(self, _request):
            raise InterruptedError('request interrupted')

    monkeypatch.setattr(
        'urllib.request.build_opener',
        lambda *_handlers: InterruptedOpener(),
    )
    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'payment gateway unavailable\n'


def test_http_gateway_preserves_interruption_as_the_cause(monkeypatch):
    class InterruptedOpener:
        def open(self, _request):
            raise InterruptedError('request interrupted')

    monkeypatch.setattr(
        'urllib.request.build_opener',
        lambda *_handlers: InterruptedOpener(),
    )

    with pytest.raises(InterruptedPayment) as raised:
        HttpPaymentGateway().charge('L1')

    assert isinstance(raised.value.__cause__, InterruptedError)


def test_http_gateway_preserves_interruption_wrapped_in_url_error(monkeypatch):
    interruption = InterruptedError('request interrupted')

    class InterruptedOpener:
        def open(self, _request):
            raise URLError(interruption)

    monkeypatch.setattr('urllib.request.build_opener', lambda *_handlers: InterruptedOpener())

    with pytest.raises(InterruptedPayment) as raised:
        HttpPaymentGateway().charge('L1')

    assert raised.value.__cause__ is interruption


def test_http_gateway_uses_configured_default_url(monkeypatch):
    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self):
            return b'charged\n'

    class Opener:
        def open(self, payment_request):
            assert (
                payment_request.full_url
                == 'https://payments.lending-library.invalid/charge?loan=L1'
            )
            assert payment_request.get_method() == 'POST'
            assert payment_request.data == b''
            return Response()

    monkeypatch.delenv('PAYMENT_GATEWAY_URL', raising=False)
    monkeypatch.setattr('urllib.request.build_opener', lambda *_handlers: Opener())

    assert HttpPaymentGateway().charge('L1') == GatewayResponse(200, 'charged\n')


@pytest.mark.django_db
def test_io_failure_is_returned_as_gateway_unavailable(client, monkeypatch):
    class FailedOpener:
        def open(self, _request):
            raise OSError('connection unavailable')

    monkeypatch.setattr(
        'urllib.request.build_opener',
        lambda *_handlers: FailedOpener(),
    )
    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'payment gateway unavailable\n'
