import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest


@pytest.fixture
def payment_gateway(monkeypatch):
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            self.server.requests.append((self.command, self.path, body))
            status, response_body = (
                (503, b'declined\n')
                if self.path == '/charge?loan=L2'
                else (200, b'charged\n')
            )
            self.send_response(status)
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
def test_fee_page_offers_htmx_payment_and_configures_error_swaps(client):
    response = client.get('/ui/fees/L3/')
    body = response.content.decode()

    assert response.status_code == 200
    assert 'Late fee for L3' in body
    assert 'Fee: $4.75' in body
    assert 'hx-post="/ui/payments/L3/"' in body
    assert '"[45].."' in body


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
def test_payment_api_does_not_call_gateway_for_unknown_loan(client, payment_gateway):
    response = client.post('/payments/unknown')

    assert (response.status_code, response.content.decode()) == (404, 'no such loan\n')
    assert payment_gateway.requests == []


@pytest.mark.django_db
def test_payment_page_swaps_gateway_error_fragment(client, payment_gateway):
    response = client.post(
        '/ui/payments/L2/',
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/html'
    assert 'Payment could not be completed' in response.content.decode()
    assert 'declined' in response.content.decode()


@pytest.mark.django_db
def test_interrupted_payment_is_a_gateway_failure_without_losing_interrupt(
    client, monkeypatch
):
    def interrupt(_request):
        raise InterruptedError('request interrupted')

    monkeypatch.setattr('urllib.request.urlopen', interrupt)
    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content.decode() == 'payment gateway unavailable\n'
