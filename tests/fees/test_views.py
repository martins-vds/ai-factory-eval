import json
import urllib.request
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

import pytest
from django.urls import reverse
from django.utils import timezone
from playwright.sync_api import sync_playwright

from src.loans.models import Loan

HTTP_GOLDENS = json.loads(
    (
        Path(__file__).resolve().parents[2] / '.migration/characterization/source/goldens/http.json'
    ).read_text(encoding='utf-8')
)
EDGE_CASE_GOLDENS = json.loads(
    (
        Path(__file__).resolve().parents[2]
        / '.migration/characterization/source/goldens/edge-cases.json'
    ).read_text(encoding='utf-8')
)


@pytest.fixture
def payment_gateway(monkeypatch):
    state = {'requests': [], 'status': 200, 'body': b'charged\n'}

    class GatewayHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
            state['requests'].append((self.command, self.path, body))
            self.send_response(state['status'])
            self.end_headers()
            self.wfile.write(state['body'])

        def log_message(self, format, *args):
            return

    server = ThreadingHTTPServer(('127.0.0.1', 0), GatewayHandler)
    thread = Thread(target=server.serve_forever)
    thread.start()
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', f'http://127.0.0.1:{server.server_port}')
    try:
        yield state
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


@pytest.mark.django_db
def test_fee_api_matches_characterized_response(client):
    expected = HTTP_GOLDENS['GET /fees/{id}']['response']

    response = client.get('/fees/L3')

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']


@pytest.mark.django_db
def test_fee_api_returns_characterized_not_found_response(client):
    expected = EDGE_CASE_GOLDENS['GET /fees/unknown']['response']

    response = client.get('/fees/unknown')

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']


@pytest.mark.django_db
def test_fee_api_uses_today_for_an_unreturned_loan(client):
    today = timezone.localdate()
    due_on = today - timedelta(days=3)
    Loan.objects.create(
        id='L9',
        member='reader',
        isbn='123',
        lent_on=due_on - timedelta(days=14),
    )

    response = client.get('/fees/L9')

    assert response.status_code == 200
    assert response.content.decode() == (
        f'<h1>Late fee for L9</h1><p>Due {due_on.isoformat()}, 3 day(s) late.</p>'
        '<p class="fee">Fee: $0.75</p>'
    )


@pytest.mark.django_db
def test_fee_api_and_page_cap_the_fee_at_ten_dollars(client):
    due_on = date(2026, 1, 15)
    Loan.objects.create(
        id='L9',
        member='reader',
        isbn='123',
        lent_on=date(2026, 1, 1),
        returned_on=due_on + timedelta(days=40),
    )

    api_response = client.get('/fees/L9')
    page_response = client.get('/ui/fees/L9/')

    assert b'Fee: $10.00' in api_response.content
    assert b'Fee: $10.00' in page_response.content


@pytest.mark.django_db
def test_fee_page_returns_not_found_for_an_unknown_loan(client):
    response = client.get('/ui/fees/unknown/')

    assert response.status_code == 404
    assert response.content == b'<p>No such loan.</p>'


@pytest.mark.django_db
def test_payment_api_forwards_gateway_success_and_maps_other_statuses(
    client,
    payment_gateway,
):
    success = client.post('/payments/L1')

    assert success.status_code == 200
    assert success['Content-Type'] == 'text/plain'
    assert success.content == b'charged\n'

    payment_gateway['status'] = 503
    payment_gateway['body'] = b'declined\n'
    failure = client.post('/payments/L2')

    assert failure.status_code == 502
    assert failure['Content-Type'] == 'text/plain'
    assert failure.content == b'declined\n'
    assert payment_gateway['requests'] == [
        ('POST', '/charge?loan=L1', b''),
        ('POST', '/charge?loan=L2', b''),
    ]


@pytest.mark.django_db
def test_payment_api_does_not_call_gateway_for_an_unknown_loan(
    client,
    payment_gateway,
):
    expected = EDGE_CASE_GOLDENS['POST /payments/unknown']['response']

    response = client.post('/payments/unknown')

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']
    assert payment_gateway['requests'] == []


@pytest.mark.django_db
def test_interrupted_payment_is_a_gateway_failure_without_losing_the_interruption(
    client,
    monkeypatch,
    caplog,
):
    def interrupt(*args, **kwargs):
        raise InterruptedError('request interrupted')

    monkeypatch.setattr(urllib.request, 'urlopen', interrupt)

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'
    assert 'InterruptedError: request interrupted' in caplog.text
    assert 'Payment gateway request failed' in caplog.text
    ui_response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')
    assert ui_response.status_code == 502
    assert b'Payment gateway unavailable.' in ui_response.content


@pytest.mark.django_db
def test_payment_api_maps_gateway_connection_failures(client, monkeypatch):
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', 'http://127.0.0.1:1')

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'


@pytest.mark.django_db
def test_fee_page_uses_reading_room_layout_and_supports_htmx_payment(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'Late fee for L3' in response.content
    assert b'ISBN 9781617294945' in response.content
    assert b'Fee: $4.75' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content
    assert b'htmx:beforeSwap' in response.content


@pytest.mark.django_db
def test_payment_redirect_keeps_loan_id_inside_the_fee_page_route(
    client,
    payment_gateway,
):
    loan_id = 'https:attacker.example'
    Loan.objects.create(
        id=loan_id,
        member='reader',
        isbn='123',
        lent_on=date(2026, 1, 1),
    )

    response = client.post(f'/ui/payments/{loan_id}/')

    assert response.status_code == 302
    assert response['Location'] == reverse('fee_page', kwargs={'loan_id': loan_id})


@pytest.mark.django_db
def test_fee_page_payment_shows_success_and_gateway_failure(
    client,
    payment_gateway,
):
    success = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert success.status_code == 200
    assert b'role="status"' in success.content
    assert b'Payment received.' in success.content

    payment_gateway['status'] = 503
    payment_gateway['body'] = b'declined\n'
    failure = client.post('/ui/payments/L2/', HTTP_HX_REQUEST='true')

    assert failure.status_code == 502
    assert b'role="alert"' in failure.content
    assert b'declined' in failure.content

    payment_gateway['body'] = b''
    empty_failure = client.post('/ui/payments/L2/', HTTP_HX_REQUEST='true')

    assert empty_failure.status_code == 502
    assert b'Payment gateway unavailable.' in empty_failure.content

    payment_gateway['body'] = b'declined\n'
    page_failure = client.post('/ui/payments/L2/')

    assert page_failure.status_code == 502
    assert b'role="alert"' in page_failure.content
    assert b'declined' in page_failure.content


@pytest.mark.django_db
def test_ui_payment_rejects_unknown_loans_without_calling_gateway(
    client,
    payment_gateway,
):
    response = client.post('/ui/payments/unknown/', HTTP_HX_REQUEST='true')

    assert response.status_code == 404
    assert response.content == b'<p>No such loan.</p>'
    assert payment_gateway['requests'] == []


@pytest.mark.django_db
def test_real_browser_can_view_and_pay_late_fee(live_server, payment_gateway):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/fees/L3/')
            assert page.get_by_role('heading', name='Late fee for L3').is_visible()
            assert page.get_by_text('Fee: $4.75').is_visible()

            htmx_available = page.evaluate("typeof window.htmx !== 'undefined'")
            page.get_by_role('button', name='Pay late fee').click()

            if htmx_available:
                page.get_by_role('status').wait_for()
                assert page.get_by_role('status').inner_text() == 'Payment received.'
            else:
                page.wait_for_url('**/ui/fees/L3/')

            assert payment_gateway['requests'] == [('POST', '/charge?loan=L3', b'')]
        finally:
            browser.close()


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('path', 'method'),
    [
        ('/fees/L1', 'post'),
        ('/payments/L1', 'get'),
        ('/ui/fees/L1/', 'post'),
        ('/ui/payments/L1/', 'get'),
    ],
)
def test_fee_and_payment_routes_reject_unsupported_methods(
    client,
    payment_gateway,
    path,
    method,
):
    response = getattr(client, method)(path)

    assert response.status_code == 405
    assert payment_gateway['requests'] == []
