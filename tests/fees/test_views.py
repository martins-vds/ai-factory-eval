import json
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

HTTP_GOLDENS = json.loads(
    (
        Path(__file__).resolve().parents[2]
        / '.migration/characterization/source/goldens/http.json'
    ).read_text(encoding='utf-8')
)
GATEWAY_GOLDENS = json.loads(
    (
        Path(__file__).resolve().parents[2]
        / '.migration/characterization/source/goldens/gateway.json'
    ).read_text(encoding='utf-8')
)


class GatewayHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
        self.server.requests.append((self.path, body))
        if self.server.drop_connection:
            self.connection.shutdown(socket.SHUT_RDWR)
            self.connection.close()
            return

        self.send_response(self.server.response_status)
        self.end_headers()
        self.wfile.write(self.server.response_body)

    def log_message(self, format, *args):
        pass


@pytest.fixture
def gateway_server(monkeypatch):
    server = ThreadingHTTPServer(('127.0.0.1', 0), GatewayHandler)
    server.requests = []
    server.response_status = 200
    server.response_body = b'charged\n'
    server.drop_connection = False
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    monkeypatch.setenv(
        'PAYMENT_GATEWAY_URL',
        f'http://127.0.0.1:{server.server_port}',
    )
    yield server
    server.shutdown()
    thread.join()
    server.server_close()


@pytest.mark.django_db
def test_fee_api_matches_the_characterized_html_response(client):
    expected = HTTP_GOLDENS['GET /fees/{id}']['response']

    response = client.get('/fees/L3')

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']


@pytest.mark.django_db
def test_fee_api_returns_the_characterized_not_found_response(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content == b'<p>No such loan.</p>'


@pytest.mark.django_db
def test_fee_page_uses_reading_room_layout_and_posts_to_ui_payment(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'A small nudge, never a surprise' in response.content
    assert b'19 late days' in response.content
    assert b'$4.75' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content


@pytest.mark.django_db
def test_payment_api_posts_to_gateway_and_returns_success_body(client, gateway_server):
    expected = GATEWAY_GOLDENS['responses']['POST /payments/L1 via test gateway']['response']
    gateway_server.response_body = b'charged\n'

    response = client.post('/payments/L1')

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']
    assert gateway_server.requests == [
        (request['path'], request['body'].encode())
        for request in GATEWAY_GOLDENS['gateway_requests'][:1]
    ]


@pytest.mark.django_db
def test_payment_api_maps_non_success_gateway_status_to_502(client, gateway_server):
    gateway_server.response_status = 503
    gateway_server.response_body = b'declined\n'

    response = client.post('/payments/L2')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'declined\n'
    assert gateway_server.requests == [('/charge?loan=L2', b'')]


@pytest.mark.django_db
def test_payment_api_returns_not_found_without_calling_gateway(client, gateway_server):
    response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response.content == b'no such loan\n'
    assert gateway_server.requests == []


@pytest.mark.django_db
def test_payment_api_maps_gateway_io_failure_to_unavailable(client, gateway_server):
    gateway_server.drop_connection = True

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'


@pytest.mark.django_db
def test_ui_payment_renders_gateway_failure_for_htmx(client, gateway_server):
    gateway_server.response_status = 503
    gateway_server.response_body = b'declined\n'

    response = client.post(
        '/ui/payments/L2/',
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 502
    assert b'id="payment-status"' in response.content
    assert b'role="alert"' in response.content
    assert b'declined' in response.content
