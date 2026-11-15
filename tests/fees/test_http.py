import json
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

import pytest

GOLDENS = Path(__file__).resolve().parents[2] / '.migration/characterization/source/goldens'
HTTP_GOLDENS = json.loads((GOLDENS / 'http.json').read_text(encoding='utf-8'))
EDGE_GOLDENS = json.loads((GOLDENS / 'edge-cases.json').read_text(encoding='utf-8'))
GATEWAY_GOLDENS = json.loads((GOLDENS / 'gateway.json').read_text(encoding='utf-8'))


@contextmanager
def payment_gateway(status, body):
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body_length = int(self.headers.get('Content-Length', 0))
            requests.append((self.command, self.path, self.rfile.read(body_length)))
            self.send_response(status)
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}', requests
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


@pytest.mark.django_db
def test_fee_endpoint_matches_characterized_page(client):
    expected = HTTP_GOLDENS['GET /fees/{id}']['response']

    response = client.get('/fees/L3')

    assert response.status_code == expected['status']
    assert response['Content-Type'].split(';')[0] == expected['content_type']
    assert response.content.decode() == expected['body']


@pytest.mark.django_db
def test_fee_endpoint_matches_characterized_missing_loan_response(client):
    expected = EDGE_GOLDENS['GET /fees/unknown']['response']

    response = client.get('/fees/unknown')

    assert response.status_code == expected['status']
    assert response['Content-Type'].split(';')[0] == expected['content_type']
    assert response.content.decode() == expected['body']


@pytest.mark.django_db
def test_payment_endpoint_forwards_characterized_gateway_request(client, monkeypatch):
    expected = GATEWAY_GOLDENS['responses']['POST /payments/L1 via test gateway']['response']
    with payment_gateway(expected['status'], expected['body'].encode()) as (url, requests):
        monkeypatch.setenv('PAYMENT_GATEWAY_URL', url)

        response = client.post('/payments/L1')

    assert response.status_code == expected['status']
    assert response['Content-Type'].split(';')[0] == expected['content_type']
    assert response.content.decode() == expected['body']
    assert requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_payment_endpoint_maps_gateway_failure_to_characterized_response(client, monkeypatch):
    expected = GATEWAY_GOLDENS['responses']['POST /payments/L2 via test gateway']['response']
    with payment_gateway(503, expected['body'].encode()) as (url, requests):
        monkeypatch.setenv('PAYMENT_GATEWAY_URL', url)

        response = client.post('/payments/L2')

    assert response.status_code == expected['status']
    assert response['Content-Type'].split(';')[0] == expected['content_type']
    assert response.content.decode() == expected['body']
    assert requests == [('POST', '/charge?loan=L2', b'')]


@pytest.mark.django_db
def test_payment_endpoint_does_not_call_gateway_for_missing_loan(client, monkeypatch):
    with payment_gateway(200, b'charged\n') as (url, requests):
        monkeypatch.setenv('PAYMENT_GATEWAY_URL', url)

        response = client.post('/payments/unknown')

    expected = EDGE_GOLDENS['POST /payments/unknown']['response']
    assert response.status_code == expected['status']
    assert response['Content-Type'].split(';')[0] == expected['content_type']
    assert response.content.decode() == expected['body']
    assert requests == []


@pytest.mark.django_db
def test_fee_page_uses_reading_room_layout_and_htmx_payment_action(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'Late fee for L3' in response.content
    assert b'Fee: $4.75' in response.content
    assert b'class="card' in response.content
    assert b'action="/ui/payments/L3/"' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content


@pytest.mark.django_db
def test_htmx_payment_action_returns_visible_gateway_feedback(client, monkeypatch):
    with payment_gateway(200, b'charged\n') as (url, requests):
        monkeypatch.setenv('PAYMENT_GATEWAY_URL', url)

        response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="status"' in response.content
    assert b'Payment complete' in response.content
    assert requests == [('POST', '/charge?loan=L1', b'')]
