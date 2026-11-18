from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest


@pytest.fixture
def payment_gateway(monkeypatch):
    state = {'status': 200, 'body': b'charged\n', 'requests': []}

    class GatewayHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
            state['requests'].append((self.command, self.path, body))
            self.send_response(state['status'])
            self.end_headers()
            self.wfile.write(state['body'])

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), GatewayHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setenv(
        'PAYMENT_GATEWAY_URL',
        f'http://127.0.0.1:{server.server_port}',
    )

    yield state

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
def test_fee_api_returns_the_characterized_unknown_loan_response(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content == b'<p>No such loan.</p>'


@pytest.mark.django_db
def test_fee_page_shows_the_fee_and_posts_payment_to_the_ui_route(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'Late fee for L3' in response.content
    assert b'Due 2025-12-15' in response.content
    assert b'19 day(s) late' in response.content
    assert b'Fee: $4.75' in response.content
    assert b'action="/ui/payments/L3/"' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content


@pytest.mark.django_db
def test_payment_api_posts_the_characterized_request_and_forwards_success(
    client,
    payment_gateway,
):
    response = client.post('/payments/L3')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'charged\n'
    assert payment_gateway['requests'] == [('POST', '/charge?loan=L3', b'')]


@pytest.mark.django_db
def test_payment_api_maps_non_success_gateway_status_to_502(client, payment_gateway):
    payment_gateway['status'] = 503
    payment_gateway['body'] = b'declined\n'

    response = client.post('/payments/L3')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'declined\n'


@pytest.mark.django_db
def test_payment_api_does_not_call_gateway_for_an_unknown_loan(client, payment_gateway):
    response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response.content == b'no such loan\n'
    assert payment_gateway['requests'] == []


@pytest.mark.django_db
def test_payment_api_returns_502_when_the_gateway_is_unavailable(client, monkeypatch):
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', 'http://127.0.0.1:1')

    response = client.post('/payments/L3')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'


@pytest.mark.django_db
def test_htmx_payment_success_renders_a_status(payment_gateway, client):
    response = client.post('/ui/payments/L3/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="status"' in response.content
    assert b'charged' in response.content
    assert payment_gateway['requests'] == [('POST', '/charge?loan=L3', b'')]


@pytest.mark.django_db
def test_htmx_payment_failure_renders_an_alert(payment_gateway, client):
    payment_gateway['status'] = 503
    payment_gateway['body'] = b'declined\n'

    response = client.post('/ui/payments/L3/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="alert"' in response.content
    assert b'declined' in response.content


@pytest.mark.django_db
def test_browser_payment_failure_renders_a_full_error_page(payment_gateway, client):
    payment_gateway['status'] = 503
    payment_gateway['body'] = b'declined\n'

    response = client.post('/ui/payments/L3/')

    assert response.status_code == 502
    assert b'<!doctype html>' in response.content
    assert b'role="alert"' in response.content
    assert b'declined' in response.content
    assert b'href="/ui/fees/L3/"' in response.content


@pytest.mark.django_db
def test_unknown_fee_page_renders_a_not_found_page(client):
    response = client.get('/ui/fees/unknown/')

    assert response.status_code == 404
    assert b'No such loan' in response.content
