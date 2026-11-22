import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from typing import ClassVar
from urllib.parse import parse_qs, urlsplit

import pytest


@pytest.fixture
def payment_gateway(monkeypatch):
    class Handler(BaseHTTPRequestHandler):
        requests: ClassVar[list[tuple[str, str, bytes]]] = []

        def do_POST(self):
            body = self.rfile.read(int(self.headers.get('Content-Length', '0')))
            self.requests.append((self.command, self.path, body))
            loan_id = parse_qs(urlsplit(self.path).query)['loan'][0]
            status, response_body = {
                'L1': (200, b'charged\n'),
                'L2': (503, b'declined\n'),
                'L3': (302, b'redirected\n'),
            }[loan_id]
            self.send_response(status)
            if status == 302:
                self.send_header('Location', '/charge?loan=L1')
            self.end_headers()
            self.wfile.write(response_body)

        def log_message(self, format, *args):
            pass

    Handler.requests = []
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = Thread(target=server.serve_forever)
    thread.start()
    monkeypatch.setenv(
        'PAYMENT_GATEWAY_URL',
        f'http://127.0.0.1:{server.server_port}',
    )
    try:
        yield Handler.requests
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


@pytest.mark.django_db
def test_fee_api_matches_the_characterized_html(client):
    response = client.get('/fees/L3')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html; charset=utf-8'
    assert response.content.decode() == (
        '<h1>Late fee for L3</h1><p>Due 2025-12-15, 19 day(s) late.</p>'
        '<p class="fee">Fee: $4.75</p>'
    )


@pytest.mark.django_db
def test_fee_api_returns_the_characterized_not_found_response(client):
    response = client.get('/fees/L9')

    assert response.status_code == 404
    assert response.content.decode() == '<p>No such loan.</p>'


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('loan_id', 'status', 'body'),
    [
        ('L1', 200, 'charged\n'),
        ('L2', 502, 'declined\n'),
        ('L3', 502, 'redirected\n'),
    ],
)
def test_payment_api_forwards_gateway_request_and_result(
    client, payment_gateway, loan_id, status, body
):
    response = client.post(f'/payments/{loan_id}')

    assert response.status_code == status
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == body
    assert payment_gateway == [('POST', f'/charge?loan={loan_id}', b'')]


@pytest.mark.django_db
def test_payment_api_rejects_unknown_loan_without_calling_gateway(client, payment_gateway):
    response = client.post('/payments/L9')

    assert response.status_code == 404
    assert response.content.decode() == 'no such loan\n'
    assert payment_gateway == []


@pytest.mark.django_db
def test_fee_page_shows_the_reading_room_layout_and_htmx_payment_action(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'Due 2025-12-15' in response.content
    assert b'Late fee for L3' in response.content
    assert b'19 day(s) late' in response.content
    assert b'Fee: $4.75' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content
    assert b'hx-on::response-error=' in response.content


@pytest.mark.django_db
def test_fee_page_returns_the_reading_room_not_found_page(client):
    response = client.get('/ui/fees/L9/')

    assert response.status_code == 404
    assert b'No such loan.' in response.content


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('path', 'method'),
    [
        ('/fees/L3', 'post'),
        ('/ui/fees/L3/', 'post'),
        ('/payments/L3', 'get'),
        ('/ui/payments/L3/', 'get'),
    ],
)
def test_fee_and_payment_routes_reject_unsupported_methods(client, path, method):
    response = getattr(client, method)(path)

    assert response.status_code == 405


@pytest.mark.django_db
def test_ui_payment_shows_gateway_failure_to_htmx(client, payment_gateway):
    response = client.post('/ui/payments/L2/', HTTP_HX_REQUEST='true')

    assert response.status_code == 502
    assert b'role="alert"' in response.content
    assert b'declined' in response.content
    assert payment_gateway == [('POST', '/charge?loan=L2', b'')]


@pytest.mark.django_db
def test_ui_payment_returns_success_to_htmx(client, payment_gateway):
    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="status"' in response.content
    assert b'charged' in response.content
    assert payment_gateway == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_ui_payment_returns_a_full_page_without_an_htmx_request(client, payment_gateway):
    response = client.post('/ui/payments/L1/')

    assert response.status_code == 200
    assert b'<title>Payment' in response.content
    assert b'role="status"' in response.content
    assert b'charged' in response.content
    assert b'/ui/fees/L1/' in response.content
    assert payment_gateway == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_ui_payment_returns_unknown_loan_as_htmx_error(client):
    response = client.post('/ui/payments/L9/', HTTP_HX_REQUEST='true')

    assert response.status_code == 404
    assert b'role="alert"' in response.content
    assert b'No such loan.' in response.content


@pytest.mark.django_db
def test_ui_payment_returns_unknown_loan_as_a_full_page(client):
    response = client.post('/ui/payments/L9/')

    assert response.status_code == 404
    assert b'<title>Payment' in response.content
    assert b'role="alert"' in response.content
    assert b'No such loan.' in response.content


@pytest.mark.django_db
def test_payment_api_preserves_interruption_when_returning_gateway_failure(
    client, monkeypatch, caplog
):
    def interrupt(_request):
        raise InterruptedError('request interrupted')

    monkeypatch.setattr('src.fees.gateway.urlopen', interrupt)
    with caplog.at_level(logging.ERROR, logger='src.fees.views'):
        response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content.decode() == 'payment gateway unavailable\n'
    payment_error = next(record for record in caplog.records if record.exc_info)
    assert isinstance(payment_error.exc_info[1].__cause__, InterruptedError)
