from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest
from playwright.sync_api import sync_playwright


@contextmanager
def payment_gateway(status, body):
    requests = []
    response_body = body.encode()

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            requests.append(
                (
                    self.command,
                    self.path,
                    self.rfile.read(int(self.headers.get('Content-Length', 0))),
                )
            )
            self.send_response(status)
            self.send_header('Content-Length', str(len(response_body)))
            self.end_headers()
            self.wfile.write(response_body)

        def log_message(self, format, *args):
            return

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
def test_fee_api_renders_the_characterized_html_fragment(client):
    response = client.get('/fees/L3')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == (
        '<h1>Late fee for L3</h1>'
        '<p>Due 2025-12-15, 19 day(s) late.</p>'
        '<p class="fee">Fee: $4.75</p>'
    )


@pytest.mark.django_db
def test_fee_api_returns_the_characterized_not_found_response(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == '<p>No such loan.</p>'


@pytest.mark.django_db
def test_fee_page_shows_loan_fee_and_payment_action(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'Late fee for L3' in response.content
    assert b'Due Dec 15, 2025' in response.content
    assert b'19 day(s) late' in response.content
    assert b'$4.75' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content
    assert b'hx-on::response-error=' in response.content


@pytest.mark.django_db
def test_unknown_fee_page_renders_not_found(client):
    response = client.get('/ui/fees/unknown/')

    assert response.status_code == 404
    assert b'<html' in response.content
    assert b'role="alert"' in response.content
    assert b'No such loan.' in response.content


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('gateway_status', 'gateway_body', 'expected_status'),
    [(200, 'charged\n', 200), (503, 'declined\n', 502)],
)
def test_payment_api_posts_to_the_gateway_and_maps_its_response(
    client, monkeypatch, gateway_status, gateway_body, expected_status
):
    with payment_gateway(gateway_status, gateway_body) as (gateway_url, requests):
        monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

        response = client.post('/payments/L1')

    assert response.status_code == expected_status
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == gateway_body
    assert requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_payment_api_returns_gateway_unavailable_on_connection_failure(client, monkeypatch):
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', 'http://127.0.0.1:1')

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content.decode() == 'payment gateway unavailable\n'


@pytest.mark.django_db
def test_payment_api_returns_not_found_without_calling_gateway(client, monkeypatch):
    with payment_gateway(200, 'charged\n') as (gateway_url, requests):
        monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

        response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response.content.decode() == 'no such loan\n'
    assert requests == []


@pytest.mark.django_db
def test_htmx_payment_success_renders_a_status_fragment(client, monkeypatch):
    with payment_gateway(200, 'charged\n') as (gateway_url, requests):
        monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

        response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'<p role="status">Payment complete: charged' in response.content
    assert requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_htmx_payment_failure_renders_an_error_fragment(client, monkeypatch):
    with payment_gateway(503, 'declined\n') as (gateway_url, requests):
        monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

        response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 502
    assert b'<p role="alert">' in response.content
    assert b'Payment could not be completed: declined' in response.content
    assert requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_htmx_payment_for_unknown_loan_renders_not_found_without_gateway(client, monkeypatch):
    with payment_gateway(200, 'charged\n') as (gateway_url, requests):
        monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

        response = client.post('/ui/payments/unknown/', HTTP_HX_REQUEST='true')

    assert response.status_code == 404
    assert b'<p role="alert">Payment could not be completed: No such loan.' in response.content
    assert requests == []


@pytest.mark.django_db
def test_browser_can_see_a_payment_gateway_failure(live_server, monkeypatch):
    with payment_gateway(503, 'declined\n') as (gateway_url, requests):
        monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                page = browser.new_page()
                page.goto(f'{live_server.url}/ui/fees/L3/')
                assert page.get_by_role('heading', name='Late fee for L3').is_visible()

                page.get_by_role('button', name='Pay late fee').click()

                alert = page.get_by_role('alert')
                alert.wait_for()
                assert 'Payment could not be completed: declined' in alert.inner_text()
            finally:
                browser.close()

    assert requests == [('POST', '/charge?loan=L3', b'')]
