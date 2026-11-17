import json
import re
import threading
from contextlib import contextmanager
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

import pytest
from playwright.sync_api import sync_playwright

from src.fees.gateway import PaymentGatewayError, charge_loan
from src.loans.models import Loan

HTTP_GOLDEN_PATH = (
    Path(__file__).resolve().parents[2] / '.migration/characterization/source/goldens/http.json'
)
HTTP_GOLDENS = json.loads(HTTP_GOLDEN_PATH.read_text(encoding='utf-8'))
EDGE_CASES_PATH = (
    Path(__file__).resolve().parents[2]
    / '.migration/characterization/source/goldens/edge-cases.json'
)
EDGE_CASES = json.loads(EDGE_CASES_PATH.read_text(encoding='utf-8'))


@contextmanager
def payment_gateway(status, body):
    requests = []

    class GatewayHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            requests.append(
                {
                    'method': self.command,
                    'path': self.path,
                    'body': self.rfile.read(int(self.headers.get('Content-Length', 0))).decode(),
                }
            )
            self.send_response(status)
            self.send_header('Content-Type', 'text/plain')
            if 300 <= status < 400:
                self.send_header('Location', '/redirected')
            self.end_headers()
            self.wfile.write(body.encode())

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), GatewayHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}', requests
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


@pytest.mark.django_db
def test_fee_api_matches_the_characterized_page_for_an_existing_loan(client):
    golden = HTTP_GOLDENS['GET /fees/{id}']

    response = client.get(golden['request']['path'])

    assert response.status_code == golden['response']['status']
    assert response['Content-Type'] == golden['response']['content_type']
    assert response.content.decode() == golden['response']['body']


@pytest.mark.django_db
@pytest.mark.parametrize(('days_late', 'amount'), [(2, '0.00'), (3, '0.75')])
def test_fee_api_waives_only_two_days_and_charges_all_late_days_after(
    client, days_late, amount
):
    loan = Loan.objects.create(
        id=f'F{days_late}',
        member='reader',
        isbn='123',
        lent_on=date(2026, 1, 1),
        returned_on=date(2026, 1, 15) + timedelta(days=days_late),
    )

    response = client.get(f'/fees/{loan.id}')

    assert response.status_code == 200
    assert response.content.decode() == (
        f'<h1>Late fee for {loan.id}</h1>'
        f'<p>Due 2026-01-15, {days_late} day(s) late.</p>'
        f'<p class="fee">Fee: ${amount}</p>'
    )


@pytest.mark.django_db
@pytest.mark.parametrize(('loan_id', 'amount'), [('L1', '$10.00'), ('L2', '$0.00')])
def test_fee_api_caps_fees_and_uses_the_return_date(client, loan_id, amount):
    response = client.get(f'/fees/{loan_id}')

    assert response.status_code == 200
    assert response.content.decode().endswith(f'Fee: {amount}</p>')


@pytest.mark.django_db
def test_fee_api_returns_the_characterized_not_found_response(client):
    golden = EDGE_CASES['GET /fees/unknown']

    response = client.get(golden['request']['path'])

    assert response.status_code == golden['response']['status']
    assert response['Content-Type'] == golden['response']['content_type']
    assert response.content.decode() == golden['response']['body']


@pytest.mark.django_db
def test_payment_api_forwards_the_characterized_request_to_the_gateway(
    client, monkeypatch
):
    with payment_gateway(200, 'charged\n') as (gateway_url, requests):
        monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

        response = client.post('/payments/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'charged\n'
    assert requests == [{'method': 'POST', 'path': '/charge?loan=L1', 'body': ''}]


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('gateway_status', 'body'),
    [(503, 'declined\n'), (302, 'redirected\n')],
)
def test_payment_api_maps_non_success_gateway_responses_to_502(
    client, monkeypatch, gateway_status, body
):
    with payment_gateway(gateway_status, body) as (gateway_url, requests):
        monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

        response = client.post('/payments/L2')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content == body.encode()
    assert requests == [{'method': 'POST', 'path': '/charge?loan=L2', 'body': ''}]


@pytest.mark.django_db
def test_payment_api_does_not_call_gateway_for_an_unknown_loan(client, monkeypatch):
    with payment_gateway(200, 'charged\n') as (gateway_url, requests):
        monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

        response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'no such loan\n'
    assert requests == []


def test_interrupted_gateway_call_keeps_the_interruption_as_its_cause():
    interruption = InterruptedError('gateway request interrupted')
    with patch('src.fees.gateway.build_opener') as build_opener:
        build_opener.return_value.open.side_effect = interruption

        with pytest.raises(PaymentGatewayError) as failure:
            charge_loan('L1')

    assert failure.value.__cause__ is interruption


@pytest.mark.django_db
def test_payment_api_returns_gateway_failure_when_the_call_is_interrupted(client):
    with patch('src.fees.gateway.build_opener') as build_opener:
        build_opener.return_value.open.side_effect = InterruptedError(
            'gateway request interrupted'
        )

        response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'


@pytest.mark.django_db
def test_payment_api_returns_gateway_failure_when_the_gateway_is_unavailable(client):
    with patch('src.fees.gateway.build_opener') as build_opener:
        build_opener.return_value.open.side_effect = OSError('connection refused')

        response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'


@pytest.mark.django_db
def test_fee_page_uses_reading_room_layout_and_htmx_payment_action(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'A small nudge, never a surprise' in response.content
    assert re.search(rb'<h1 class="[^"]*text-5xl[^"]*">Late fees</h1>', response.content)
    assert b'19 late days' in response.content
    assert b'$4.75' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content
    assert b'hx-target="#payment-status"' in response.content


@pytest.mark.django_db
def test_htmx_payment_action_displays_the_gateway_result(client, monkeypatch):
    with payment_gateway(200, 'charged\n') as (gateway_url, requests):
        monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

        response = client.post('/ui/payments/L3/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="status"' in response.content
    assert b'Payment received' in response.content
    assert b'charged' in response.content
    assert requests == [{'method': 'POST', 'path': '/charge?loan=L3', 'body': ''}]


@pytest.mark.django_db
def test_htmx_payment_action_displays_gateway_failure(client, monkeypatch):
    with payment_gateway(503, 'declined\n') as (gateway_url, requests):
        monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

        response = client.post('/ui/payments/L3/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="alert"' in response.content
    assert b'Payment could not be completed: declined' in response.content
    assert requests == [{'method': 'POST', 'path': '/charge?loan=L3', 'body': ''}]


@pytest.mark.django_db
def test_fee_page_loads_in_a_real_browser(live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            response = page.goto(f'{live_server.url}/ui/fees/L3/')

            assert response is not None
            assert response.status == 200
            assert page.get_by_role('heading', name='Late fees').is_visible()
            assert page.get_by_role('article').get_by_text('$4.75').is_visible()
            assert page.get_by_role('button', name='Pay late fee').is_visible()
        finally:
            browser.close()
