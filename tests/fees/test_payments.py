from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest

from src.fees.services import PaymentApplication


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
def test_payment_endpoint_sends_characterized_request_and_forwards_success(
    client, payment_gateway
):
    response = client.post('/payments/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'charged\n'
    assert payment_gateway['request'] == ('POST', '/charge?loan=L1', b'')


@pytest.mark.django_db
def test_payment_endpoint_maps_gateway_failure_to_502_and_preserves_body(
    client, payment_gateway
):
    payment_gateway['status'] = 503
    payment_gateway['body'] = b'declined\n'

    response = client.post('/payments/L2')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'declined\n'
    assert payment_gateway['request'] == ('POST', '/charge?loan=L2', b'')


@pytest.mark.django_db
def test_payment_endpoint_does_not_call_gateway_for_unknown_loan(
    client, payment_gateway
):
    response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response.content.decode() == 'no such loan\n'
    assert payment_gateway['request'] is None


@pytest.mark.django_db
def test_payment_endpoint_maps_connection_failure_to_characterized_502(
    client, monkeypatch
):
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


@pytest.mark.django_db
def test_htmx_payment_action_renders_success_fragment(client, payment_gateway):
    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'<!doctype html>' not in response.content
    assert b'id="payment-status"' in response.content
    assert b'role="status"' in response.content
    assert b'charged' in response.content
