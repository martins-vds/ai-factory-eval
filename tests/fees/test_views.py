from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest

import src.fees.gateway as gateway_module
from src.fees.gateway import PaymentGateway, PaymentGatewayFailure


@pytest.fixture
def local_gateway(monkeypatch):
    class GatewayHandler(BaseHTTPRequestHandler):
        calls = []
        status_code = 200
        response_body = b'charged\n'

        def do_POST(self):
            self.calls.append((self.command, self.path))
            self.send_response(self.status_code)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(self.response_body)

        def log_message(self, _format, *_args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), GatewayHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setenv(
        'PAYMENT_GATEWAY_URL',
        f'http://127.0.0.1:{server.server_port}',
    )
    GatewayHandler.calls = []
    GatewayHandler.status_code = 200
    GatewayHandler.response_body = b'charged\n'
    try:
        yield GatewayHandler
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


@pytest.mark.django_db
def test_fee_api_matches_characterized_html(client):
    response = client.get('/fees/L3')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == (
        '<h1>Late fee for L3</h1><p>Due 2025-12-15, 19 day(s) late.</p>'
        '<p class="fee">Fee: $4.75</p>'
    )


@pytest.mark.django_db
def test_fee_api_returns_characterized_not_found_response(client):
    response = client.get('/fees/missing')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == '<p>No such loan.</p>'


@pytest.mark.django_db
def test_fee_page_shows_amount_and_payment_action(client):
    response = client.get('/ui/fees/L3/')
    body = response.content.decode()

    assert response.status_code == 200
    assert '19 day(s) late' in body
    assert '$4.75' in body
    assert 'hx-post="/ui/payments/L3/"' in body
    assert 'hx-on::before-swap=' in body


@pytest.mark.django_db
def test_payment_api_forwards_gateway_success_and_request(client, local_gateway):
    response = client.post('/payments/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'charged\n'
    assert local_gateway.calls == [('POST', '/charge?loan=L1')]


@pytest.mark.django_db
def test_payment_api_maps_gateway_failure_to_bad_gateway(client, local_gateway):
    local_gateway.status_code = 503
    local_gateway.response_body = b'declined\n'

    response = client.post('/payments/L2')

    assert response.status_code == 502
    assert response.content.decode() == 'declined\n'
    assert local_gateway.calls == [('POST', '/charge?loan=L2')]


@pytest.mark.django_db
def test_payment_for_unknown_loan_does_not_call_gateway(client, local_gateway):
    response = client.post('/payments/missing')

    assert response.status_code == 404
    assert response.content.decode() == 'no such loan\n'
    assert local_gateway.calls == []


@pytest.mark.django_db
def test_payment_ui_renders_gateway_failure_for_htmx(client, local_gateway):
    local_gateway.status_code = 503
    local_gateway.response_body = b'declined\n'

    response = client.post('/ui/payments/L2/', HTTP_HX_REQUEST='true')

    assert response.status_code == 502
    assert 'role="alert"' in response.content.decode()
    assert 'declined' in response.content.decode()


def test_interrupted_gateway_call_is_wrapped_without_losing_interrupt(monkeypatch):
    interrupted = InterruptedError('request interrupted')

    class InterruptingOpener:
        def open(self, _request):
            raise interrupted

    monkeypatch.setattr(gateway_module, 'build_opener', lambda *_handlers: InterruptingOpener())

    with pytest.raises(PaymentGatewayFailure) as error:
        PaymentGateway('https://payments.example').charge('L1')

    assert error.value.__cause__ is interrupted
