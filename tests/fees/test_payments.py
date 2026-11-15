from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.error import URLError

import pytest

from src.loans.models import Loan


@pytest.fixture
def payment_gateway(monkeypatch):
    requests = []
    gateway_response = {'status': 200, 'body': b'charged\n'}

    class GatewayHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
            requests.append((self.command, self.path, body))
            self.send_response(gateway_response['status'])
            self.end_headers()
            self.wfile.write(gateway_response['body'])

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), GatewayHandler)
    thread = Thread(target=server.serve_forever)
    thread.start()
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', f'http://127.0.0.1:{server.server_port}')
    try:
        yield gateway_response, requests
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


@pytest.mark.django_db
def test_payment_api_posts_to_gateway_and_forwards_success_response(client, payment_gateway):
    _, requests = payment_gateway
    Loan.objects.get(pk='L3')

    response = client.post('/payments/L3')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'charged\n'
    assert requests == [('POST', '/charge?loan=L3', b'')]


@pytest.mark.django_db
def test_payment_api_maps_non_success_gateway_response_to_bad_gateway(client, payment_gateway):
    gateway_response, requests = payment_gateway
    gateway_response.update(status=503, body=b'declined\n')
    Loan.objects.get(pk='L3')

    response = client.post('/payments/L3')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'declined\n'
    assert requests == [('POST', '/charge?loan=L3', b'')]


@pytest.mark.django_db
def test_payment_api_does_not_call_gateway_for_unknown_loan(client, payment_gateway):
    _, requests = payment_gateway

    response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response.content == b'no such loan\n'
    assert requests == []


@pytest.mark.django_db
def test_payment_api_maps_gateway_io_failure_to_unavailable(client, monkeypatch):
    Loan.objects.get(pk='L3')
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', 'http://127.0.0.1:1')

    response = client.post('/payments/L3')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'


@pytest.mark.django_db
def test_payment_api_maps_interrupted_gateway_call_and_retains_interruption(
    client, payment_gateway, monkeypatch, caplog
):
    Loan.objects.get(pk='L3')

    def interrupted_request(*args, **kwargs):
        raise InterruptedError('request interrupted')

    monkeypatch.setattr('src.fees.services.urlopen', interrupted_request)
    response = client.post('/payments/L3')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'
    assert any(
        record.exc_info and isinstance(record.exc_info[1], InterruptedError)
        for record in caplog.records
    )


@pytest.mark.django_db
def test_payment_api_retains_interruption_wrapped_by_url_error(
    client, payment_gateway, monkeypatch, caplog
):
    Loan.objects.get(pk='L3')

    def interrupted_request(*args, **kwargs):
        raise URLError(InterruptedError('request interrupted'))

    monkeypatch.setattr('src.fees.services.urlopen', interrupted_request)
    response = client.post('/payments/L3')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'
    assert any(
        record.exc_info
        and isinstance(record.exc_info[1], URLError)
        and isinstance(record.exc_info[1].reason, InterruptedError)
        for record in caplog.records
    )


@pytest.mark.django_db
def test_htmx_payment_action_renders_success_status(client, payment_gateway):
    Loan.objects.get(pk='L3')

    response = client.post('/ui/payments/L3/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="status"' in response.content
    assert b'Payment complete' in response.content
    assert b'charged' in response.content


@pytest.mark.django_db
def test_htmx_payment_action_swaps_gateway_failure_message(client, payment_gateway):
    gateway_response, _ = payment_gateway
    gateway_response.update(status=503, body=b'declined\n')
    Loan.objects.get(pk='L3')

    response = client.post('/ui/payments/L3/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="alert"' in response.content
    assert b'declined' in response.content


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('path', 'method'),
    [
        ('/fees/L3', 'post'),
        ('/payments/L3', 'get'),
        ('/ui/fees/L3/', 'post'),
        ('/ui/payments/L3/', 'get'),
    ],
)
def test_fee_and_payment_routes_reject_unsupported_methods(client, payment_gateway, path, method):
    response = getattr(client, method)(path)

    assert response.status_code == 405
    assert payment_gateway[1] == []
