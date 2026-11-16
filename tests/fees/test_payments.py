import logging
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import URLError

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
def test_payment_api_appends_charge_path_to_gateway_base_url(client, payment_gateway, monkeypatch):
    monkeypatch.setenv(
        'PAYMENT_GATEWAY_URL',
        f'http://127.0.0.1:{payment_gateway.server_port}/pathX/',
    )

    response = client.post('/payments/L1')

    assert response.status_code == 200
    assert payment_gateway.requests == [('POST', '/pathX//charge?loan=L1', b'')]


@pytest.mark.django_db
def test_payment_api_uses_the_characterized_default_gateway_url(client, monkeypatch):
    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, exception_type, exception, traceback):
            return False

        def read(self):
            return b'charged\n'

    requests = []

    def open_gateway(request):
        requests.append(request)
        return Response()

    monkeypatch.delenv('PAYMENT_GATEWAY_URL', raising=False)
    monkeypatch.setattr('src.fees.gateway.urlopen', open_gateway)

    response = client.post('/payments/L1')

    assert response.status_code == 200
    assert requests[0].full_url == 'https://payments.lending-library.invalid/charge?loan=L1'
    assert requests[0].data == b''


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
def test_payment_api_maps_a_non_200_gateway_response_to_502(client, payment_gateway):
    payment_gateway.response_status = 201
    payment_gateway.response_body = b'created\n'

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'created\n'


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
        record.getMessage() == 'Payment gateway request was interrupted'
        and record.exc_info
        and isinstance(record.exc_info[1].__cause__, InterruptedError)
        for record in caplog.records
    )


@pytest.mark.django_db
def test_payment_api_maps_gateway_io_failure_to_unavailable(client, monkeypatch):
    def fail(request):
        raise URLError('connection failed')

    monkeypatch.setattr('src.fees.gateway.urlopen', fail)

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'


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


@pytest.mark.django_db
def test_htmx_payment_action_replaces_invalid_gateway_text(client, payment_gateway):
    payment_gateway.response_body = b'\xff'

    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'Payment complete: \xef\xbf\xbd' in response.content


@pytest.mark.django_db
def test_regular_payment_submission_renders_a_success_page(client, payment_gateway):
    response = client.post('/ui/payments/L1/')

    assert response.status_code == 200
    assert b'<!doctype html>' in response.content
    assert b'Payment complete: charged' in response.content
    assert b'href="/ui/fees/L1/"' in response.content


@pytest.mark.django_db
def test_regular_payment_submission_renders_gateway_failure(client, payment_gateway):
    payment_gateway.response_status = 503
    payment_gateway.response_body = b'declined\n'

    response = client.post('/ui/payments/L2/')

    assert response.status_code == 502
    assert b'role="alert"' in response.content
    assert b'Payment failed: declined' in response.content


@pytest.mark.django_db
def test_ui_payment_does_not_call_gateway_for_an_unknown_loan(client, payment_gateway):
    response = client.post('/ui/payments/unknown/', HTTP_HX_REQUEST='true')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'no such loan\n'
    assert payment_gateway.requests == []


@pytest.mark.parametrize(
    ('path', 'method'),
    [
        ('/payments/L1', 'get'),
        ('/ui/payments/L1/', 'get'),
    ],
)
def test_payment_routes_reject_unsupported_methods(client, path, method):
    response = getattr(client, method)(path)

    assert response.status_code == 405
