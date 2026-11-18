from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from threading import Thread

import pytest
from django.test import override_settings


HTTP_GOLDENS = json.loads(
    (
        Path(__file__).resolve().parents[2]
        / '.migration/characterization/source/goldens/http.json'
    ).read_text(encoding='utf-8')
)
EDGE_GOLDENS = json.loads(
    (
        Path(__file__).resolve().parents[2]
        / '.migration/characterization/source/goldens/edge-cases.json'
    ).read_text(encoding='utf-8')
)


@contextmanager
def payment_gateway(status, body):
    requests = []

    class GatewayHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get('Content-Length', '0'))
            requests.append((self.command, self.path, self.rfile.read(length)))
            self.send_response(status)
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), GatewayHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}', requests
    finally:
        server.shutdown()
        thread.join()


@pytest.mark.django_db
def test_fee_api_returns_the_characterized_html(client):
    expected = HTTP_GOLDENS['GET /fees/{id}']['response']

    response = client.get('/fees/L3')

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']


@pytest.mark.django_db
def test_fee_api_returns_the_characterized_not_found_response(client):
    expected = EDGE_GOLDENS['GET /fees/unknown']['response']

    response = client.get('/fees/unknown')

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']


@pytest.mark.django_db
def test_reading_room_fee_page_shows_the_fee_and_htmx_payment_form(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'Late fees</h1>' in response.content
    assert b'cy \xc2\xb7 L3' in response.content
    assert b'Dec 15, 2025' in response.content
    assert b'19 late days' in response.content
    assert b'$4.75' in response.content
    assert b'action="/ui/payments/L3/"' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content
    assert b'Pay late fee' in response.content


@pytest.mark.django_db
def test_fee_page_renders_not_found_for_an_unknown_loan(client):
    response = client.get('/ui/fees/missing/')

    assert response.status_code == 404
    assert b'No such loan.' in response.content
    assert b'href="/ui/loans/"' in response.content


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('gateway_status', 'gateway_body', 'expected_status'),
    [
        (200, b'charged\n', 200),
        (503, b'declined\n', 502),
    ],
)
def test_payment_api_uses_the_gateway_contract(
    client, gateway_status, gateway_body, expected_status
):
    with payment_gateway(gateway_status, gateway_body) as (gateway_url, requests):
        with override_settings(PAYMENT_GATEWAY_URL=gateway_url):
            response = client.post('/payments/L1')

    assert response.status_code == expected_status
    assert response['Content-Type'] == 'text/plain'
    assert response.content == gateway_body
    assert requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_payment_api_returns_not_found_without_calling_the_gateway(client):
    expected = EDGE_GOLDENS['POST /payments/unknown']['response']

    with payment_gateway(200, b'charged\n') as (gateway_url, requests):
        with override_settings(PAYMENT_GATEWAY_URL=gateway_url):
            response = client.post('/payments/unknown')

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']
    assert requests == []


@pytest.mark.django_db
def test_htmx_payment_renders_a_gateway_failure(client):
    with payment_gateway(503, b'declined\n') as (gateway_url, requests):
        with override_settings(PAYMENT_GATEWAY_URL=gateway_url):
            response = client.post(
                '/ui/payments/L3/',
                HTTP_HX_REQUEST='true',
            )

    assert response.status_code == 502
    assert b'id="payment-status"' in response.content
    assert b'role="alert"' in response.content
    assert b'declined' in response.content
    assert requests == [('POST', '/charge?loan=L3', b'')]
