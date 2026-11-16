import json
from contextlib import contextmanager
from datetime import date, timedelta
from http.client import HTTPException
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from unittest.mock import patch

import pytest
from playwright.sync_api import sync_playwright

from src.loans.models import Loan

HTTP_GOLDENS = json.loads(
    (
        Path(__file__).resolve().parents[2] / '.migration/characterization/source/goldens/http.json'
    ).read_text(encoding='utf-8')
)


@contextmanager
def payment_gateway(status=200, body=b'charged\n'):
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get('Content-Length', 0))
            requests.append(
                {
                    'method': self.command,
                    'path': self.path,
                    'body': self.rfile.read(length),
                }
            )
            self.send_response(status)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = Thread(target=server.serve_forever)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}', requests
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


@pytest.mark.django_db
def test_fee_api_returns_characterized_html(client):
    golden = HTTP_GOLDENS['GET /fees/{id}']

    response = client.get(golden['request']['path'])

    assert response.status_code == golden['response']['status']
    assert response['Content-Type'] == golden['response']['content_type']
    assert response.content.decode() == golden['response']['body']


@pytest.mark.django_db
def test_fee_api_returns_characterized_not_found_response(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content == b'<p>No such loan.</p>'


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('days_late', 'expected_days', 'expected_fee'),
    [
        (-3, 0, '0.00'),
        (2, 2, '0.00'),
        (3, 3, '0.75'),
        (39, 39, '9.75'),
        (40, 40, '10.00'),
        (100, 100, '10.00'),
    ],
)
def test_fee_api_applies_late_day_waiver_and_cap(
    client,
    days_late,
    expected_days,
    expected_fee,
):
    due_on = date(2026, 1, 1)
    loan = Loan.objects.create(
        id=f'F{days_late}',
        member='reader',
        isbn='123',
        lent_on=due_on - timedelta(days=14),
        returned_on=due_on + timedelta(days=days_late),
    )

    response = client.get(f'/fees/{loan.id}')

    assert response.status_code == 200
    assert response.content.decode() == (
        f'<h1>Late fee for {loan.id}</h1>'
        f'<p>Due {due_on.isoformat()}, {expected_days} day(s) late.</p>'
        f'<p class="fee">Fee: ${expected_fee}</p>'
    )


@pytest.mark.django_db
def test_fee_page_shows_late_fee_and_htmx_payment_action(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'Late fee for L3' in response.content
    assert b'Dec 15, 2025' in response.content
    assert b'19 day(s) late' in response.content
    assert b'$4.75' in response.content
    assert b'action="/ui/payments/L3/"' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content


@pytest.mark.django_db
def test_htmx_payment_action_shows_gateway_success(client, monkeypatch):
    with payment_gateway() as (gateway_url, gateway_requests):
        monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

        response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="status"' in response.content
    assert b'charged' in response.content
    assert gateway_requests == [{'method': 'POST', 'path': '/charge?loan=L1', 'body': b''}]


@pytest.mark.django_db
def test_htmx_payment_action_renders_gateway_failure(client, monkeypatch):
    with payment_gateway(status=503, body=b'declined\n') as (gateway_url, _):
        monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

        response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="alert"' in response.content
    assert b'declined' in response.content


@pytest.mark.django_db
def test_regular_payment_action_returns_reading_room_result_page(client, monkeypatch):
    with payment_gateway() as (gateway_url, _):
        monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

        response = client.post('/ui/payments/L1/')

    assert response.status_code == 200
    assert b'<!doctype html>' in response.content
    assert b'role="status"' in response.content
    assert b'charged' in response.content
    assert b'href="/ui/fees/L1/"' in response.content


@pytest.mark.django_db
def test_real_browser_can_view_and_pay_late_fee(live_server, monkeypatch):
    with payment_gateway() as (gateway_url, gateway_requests):
        monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                page = browser.new_page()
                page.goto(f'{live_server.url}/ui/fees/L3/')
                assert page.get_by_role('heading', name='Late fee for L3').is_visible()

                page.get_by_role('button', name='Pay late fee').click()
                page.get_by_role('status').wait_for()
                assert page.get_by_role('status').inner_text() == 'charged'
            finally:
                browser.close()

    assert gateway_requests == [{'method': 'POST', 'path': '/charge?loan=L3', 'body': b''}]


@pytest.mark.django_db
def test_payment_api_charges_existing_loan_through_gateway(client, monkeypatch):
    with payment_gateway() as (gateway_url, gateway_requests):
        monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

        response = client.post('/payments/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'charged\n'
    assert gateway_requests == [{'method': 'POST', 'path': '/charge?loan=L1', 'body': b''}]


@pytest.mark.django_db
def test_payment_api_maps_gateway_rejection_to_502_and_preserves_body(client, monkeypatch):
    with payment_gateway(status=503, body=b'declined\n') as (gateway_url, _):
        monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

        response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'declined\n'


@pytest.mark.django_db
def test_payment_api_does_not_call_gateway_for_unknown_loan(client, monkeypatch):
    with payment_gateway() as (gateway_url, gateway_requests):
        monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

        response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'no such loan\n'
    assert gateway_requests == []


@pytest.mark.django_db
@pytest.mark.parametrize('failure', [OSError, HTTPException])
def test_payment_api_maps_gateway_io_failure_to_unavailable(client, failure):
    with patch('src.fees.gateway.urlopen', side_effect=failure('disconnected')):
        response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'payment gateway unavailable\n'


@pytest.mark.django_db
def test_payment_api_keeps_interruption_as_gateway_failure(client, caplog):
    with patch(
        'src.fees.gateway.urlopen',
        side_effect=InterruptedError('request interrupted'),
    ):
        response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'
    failure_logs = [
        record
        for record in caplog.records
        if record.getMessage()
        == 'Payment gateway request was interrupted: InterruptedError: request interrupted'
    ]
    assert len(failure_logs) == 1
    assert failure_logs[0].exc_info is None
