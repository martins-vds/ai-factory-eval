import logging
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest


@pytest.fixture
def payment_gateway(monkeypatch):
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
            self.server.requests.append((self.command, self.path, body))
            self.send_response(self.server.response_status)
            self.end_headers()
            self.wfile.write(self.server.response_body)

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    server.requests = []
    server.response_status = 200
    server.response_body = b'charged\n'
    monkeypatch.setenv(
        'PAYMENT_GATEWAY_URL',
        f'http://127.0.0.1:{server.server_port}',
    )
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    yield server
    server.shutdown()
    server.server_close()
    thread.join()


@pytest.mark.django_db
def test_payment_api_posts_to_gateway_and_forwards_success(client, payment_gateway):
    response = client.post('/payments/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'charged\n'
    assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_payment_api_maps_gateway_http_failure_to_502(client, payment_gateway):
    payment_gateway.response_status = 503
    payment_gateway.response_body = b'declined\n'

    response = client.post('/payments/L2')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'declined\n'
    assert payment_gateway.requests == [('POST', '/charge?loan=L2', b'')]


@pytest.mark.django_db
def test_payment_api_does_not_call_gateway_for_an_unknown_loan(client, payment_gateway):
    response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'no such loan\n'
    assert payment_gateway.requests == []


@pytest.mark.django_db
def test_payment_api_surfaces_interruption_as_gateway_failure_without_losing_it(
    client, caplog, monkeypatch
):
    def interrupt(request):
        raise InterruptedError('request interrupted')

    monkeypatch.setattr('src.fees.gateway.urlopen', interrupt)
    with caplog.at_level(logging.ERROR, logger='src.fees.views'):
        response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'
    assert any(
        record.exc_info
        and isinstance(record.exc_info[1].__cause__, InterruptedError)
        for record in caplog.records
    )


@pytest.mark.django_db
def test_htmx_payment_action_shows_gateway_success(client, payment_gateway):
    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="status"' in response.content
    assert b'charged' in response.content
    assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_htmx_payment_action_shows_gateway_failure(client, payment_gateway):
    payment_gateway.response_status = 503
    payment_gateway.response_body = b'declined\n'

    response = client.post('/ui/payments/L2/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="alert"' in response.content
    assert b'Payment failed: declined' in response.content
