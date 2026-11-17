import json
import logging
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from types import SimpleNamespace
from urllib.error import URLError

import pytest

from src.fees.services import calculate_late_fee

HTTP_GOLDEN_PATH = (
    Path(__file__).resolve().parents[2] / '.migration/characterization/source/goldens/http.json'
)
HTTP_GOLDENS = json.loads(HTTP_GOLDEN_PATH.read_text(encoding='utf-8'))


class GatewayServer(ThreadingHTTPServer):
    def __init__(self):
        super().__init__(('127.0.0.1', 0), GatewayHandler)
        self.requests = []
        self.response_status = 200
        self.response_body = b'charged\n'


class GatewayHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
        self.server.requests.append((self.command, self.path, body))
        self.send_response(self.server.response_status)
        self.end_headers()
        self.wfile.write(self.server.response_body)

    def log_message(self, format, *args):
        pass


@pytest.fixture
def gateway_server(monkeypatch):
    server = GatewayServer()
    thread = Thread(target=server.serve_forever)
    thread.start()
    monkeypatch.setenv(
        'PAYMENT_GATEWAY_URL',
        f'http://127.0.0.1:{server.server_port}',
    )
    yield server
    server.shutdown()
    thread.join()
    server.server_close()


@pytest.mark.parametrize(
    ('days_late', 'expected_cents'),
    [(-2, 0), (0, 0), (1, 0), (2, 0), (3, 75), (19, 475), (40, 1000), (60, 1000)],
)
def test_late_fee_uses_two_day_grace_period_and_ten_dollar_cap(days_late, expected_cents):
    loan = SimpleNamespace(
        due_on=date(2026, 1, 1),
        returned_on=None,
    )

    fee = calculate_late_fee(loan, date(2026, 1, 1) + timedelta(days=days_late))

    assert fee.days_late == max(0, days_late)
    assert fee.cents == expected_cents


@pytest.mark.django_db
def test_fee_endpoint_matches_characterized_html(client):
    response = client.get('/fees/L3')
    expected = HTTP_GOLDENS['GET /fees/{id}']['response']

    assert response.status_code == expected['status']
    assert response['Content-Type'].startswith(expected['content_type'])
    assert response.content.decode() == expected['body']


@pytest.mark.django_db
def test_fee_endpoint_returns_characterized_not_found_response(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response['Content-Type'].startswith('text/html')
    assert response.content.decode() == '<p>No such loan.</p>'


@pytest.mark.django_db
def test_browser_fee_page_uses_reading_room_layout_and_payment_action(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'Late fees' in response.content
    assert b'card border' in response.content
    assert b'$4.75' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content


@pytest.mark.django_db
def test_browser_fee_page_returns_not_found_for_unknown_loan(client):
    response = client.get('/ui/fees/unknown/')

    assert response.status_code == 404


@pytest.mark.django_db
def test_payment_endpoint_calls_gateway_and_returns_success(client, gateway_server):
    response = client.post('/payments/L1')

    assert response.status_code == 200
    assert response['Content-Type'].startswith('text/plain')
    assert response.content == b'charged\n'
    assert gateway_server.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_payment_endpoint_maps_gateway_failure_to_bad_gateway(client, gateway_server):
    gateway_server.response_status = 503
    gateway_server.response_body = b'declined\n'

    response = client.post('/payments/L2')

    assert response.status_code == 502
    assert response['Content-Type'].startswith('text/plain')
    assert response.content == b'declined\n'
    assert gateway_server.requests == [('POST', '/charge?loan=L2', b'')]


@pytest.mark.django_db
def test_payment_endpoint_does_not_call_gateway_for_unknown_loan(client, gateway_server):
    response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response.content == b'no such loan\n'
    assert gateway_server.requests == []


@pytest.mark.django_db
def test_payment_endpoint_maps_gateway_io_failure_to_bad_gateway(client, monkeypatch):
    def unavailable(*args, **kwargs):
        raise URLError('offline')

    monkeypatch.setattr('src.fees.gateway.open_gateway_request', unavailable)

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'


@pytest.mark.django_db
def test_payment_endpoint_preserves_interruption_as_gateway_failure(client, monkeypatch, caplog):
    def interrupted(*args, **kwargs):
        raise InterruptedError('request interrupted')

    monkeypatch.setattr('src.fees.gateway.open_gateway_request', interrupted)

    with caplog.at_level(logging.ERROR, logger='src.fees.views'):
        response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'
    assert 'InterruptedError: request interrupted' in caplog.text


@pytest.mark.django_db
def test_browser_payment_action_uses_htmx_partial(client, gateway_server):
    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="status"' in response.content
    assert b'charged' in response.content
    assert b'<!doctype html>' not in response.content
    assert gateway_server.requests == [('POST', '/charge?loan=L1', b'')]
