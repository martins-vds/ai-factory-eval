import importlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest
from django.apps import apps
from django.db import connection
from playwright.sync_api import sync_playwright


@pytest.fixture
def local_gateway(monkeypatch):
    servers = []

    def start(status=200, body=b'charged\n'):
        requests = []

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                length = int(self.headers.get('Content-Length', '0'))
                requests.append((self.command, self.path, self.rfile.read(length)))
                self.send_response(status)
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format, *args):
                pass

        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        servers.append((server, thread))
        monkeypatch.setenv(
            'PAYMENT_GATEWAY_URL',
            f'http://127.0.0.1:{server.server_address[1]}',
        )
        return requests

    yield start

    for server, thread in servers:
        server.shutdown()
        thread.join()
        server.server_close()


@pytest.fixture
def restore_fee_seed_loans(django_db_blocker):
    yield
    with django_db_blocker.unblock():
        apps.get_model('loans', 'Loan').objects.all().delete()
        seed_loans = importlib.import_module('src.loans.migrations.0001_initial').seed_loans
        with connection.schema_editor() as schema_editor:
            seed_loans(apps, schema_editor)


@pytest.mark.django_db
def test_fee_api_returns_characterized_html(client):
    response = client.get('/fees/L3')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == (
        '<h1>Late fee for L3</h1><p>Due 2025-12-15, 19 day(s) late.</p>'
        '<p class="fee">Fee: $4.75</p>'
    )


@pytest.mark.django_db
def test_fee_api_returns_characterized_not_found_response(client):
    response = client.get('/fees/missing')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == '<p>No such loan.</p>'


@pytest.mark.django_db
def test_payment_api_posts_to_gateway_and_returns_success_body(client, local_gateway):
    requests = local_gateway()

    response = client.post('/payments/L3')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'charged\n'
    assert requests == [('POST', '/charge?loan=L3', b'')]


@pytest.mark.django_db
def test_payment_api_maps_gateway_failure_to_bad_gateway(client, local_gateway):
    requests = local_gateway(status=503, body=b'declined\n')

    response = client.post('/payments/L3')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'declined\n'
    assert requests == [('POST', '/charge?loan=L3', b'')]


@pytest.mark.django_db
def test_payment_api_rejects_missing_loan_without_calling_gateway(client, local_gateway):
    requests = local_gateway()

    response = client.post('/payments/missing')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'no such loan\n'
    assert requests == []


@pytest.mark.django_db
def test_payment_api_maps_unavailable_gateway_to_characterized_failure(client, monkeypatch):
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', 'http://127.0.0.1:1')

    response = client.post('/payments/L3')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'payment gateway unavailable\n'


@pytest.mark.django_db
def test_fee_page_uses_reading_room_layout_and_separate_payment_action(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'<h1 class="card-title mt-2 text-4xl">Late fee for L3</h1>' in response.content
    assert b'Due Dec 15, 2025, 19 day(s) late.' in response.content
    assert b'Fee: $4.75' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content
    assert b'htmx:beforeSwap' in response.content
    assert b'event.detail.shouldSwap = true' in response.content


@pytest.mark.django_db
def test_fee_page_renders_unknown_loan_as_a_not_found_page(client):
    response = client.get('/ui/fees/missing/')

    assert response.status_code == 404
    assert b'<p>No such loan.</p>' in response.content


@pytest.mark.django_db
def test_htmx_payment_success_returns_a_status_fragment(client, local_gateway):
    local_gateway()

    response = client.post('/ui/payments/L3/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'<div id="payment-status"' in response.content
    assert b'role="status">Payment received.</p>' in response.content


@pytest.mark.django_db
def test_htmx_payment_failure_renders_error_fragment_for_error_status(client, local_gateway):
    local_gateway(status=503, body=b'declined\n')

    response = client.post('/ui/payments/L3/', HTTP_HX_REQUEST='true')

    assert response.status_code == 502
    assert b'<div id="payment-status"' in response.content
    assert b'role="alert">declined\n</p>' in response.content


@pytest.mark.django_db
def test_htmx_payment_not_found_renders_error_fragment(client):
    response = client.post('/ui/payments/missing/', HTTP_HX_REQUEST='true')

    assert response.status_code == 404
    assert b'role="alert">No such loan.</p>' in response.content


@pytest.mark.django_db
def test_regular_payment_failure_renders_full_fee_page(client, local_gateway):
    local_gateway(status=503, body=b'declined\n')

    response = client.post('/ui/payments/L3/')

    assert response.status_code == 502
    assert b'<!doctype html>' in response.content
    assert b'role="alert">declined\n</p>' in response.content


@pytest.mark.django_db
@pytest.mark.usefixtures('restore_fee_seed_loans')
def test_real_browser_renders_gateway_failure(live_server, local_gateway):
    local_gateway(status=503, body=b'declined\n')

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/fees/L3/')
            page.get_by_role('button', name='Pay late fee').click()
            alert = page.get_by_role('alert')
            alert.wait_for()
            assert alert.inner_text() == 'declined'
        finally:
            browser.close()
