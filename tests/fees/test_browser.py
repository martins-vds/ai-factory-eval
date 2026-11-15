from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest
from playwright.sync_api import sync_playwright


@contextmanager
def payment_gateway():
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body_length = int(self.headers.get('Content-Length', 0))
            requests.append((self.command, self.path, self.rfile.read(body_length)))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'charged\n')

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}', requests
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


@pytest.mark.django_db
def test_browser_can_pay_a_late_fee_with_htmx_or_form_fallback(live_server, monkeypatch):
    with payment_gateway() as (url, requests):
        monkeypatch.setenv('PAYMENT_GATEWAY_URL', url)

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                page = browser.new_page()
                response = page.goto(f'{live_server.url}/ui/fees/L1/')

                assert response is not None
                assert response.status == 200
                assert page.get_by_role('heading', name='Late fee for L1').is_visible()

                htmx_available = page.evaluate("typeof window.htmx !== 'undefined'")
                page.get_by_role('button', name='Pay late fee').click()

                if htmx_available:
                    page.get_by_role('status').wait_for()
                    assert 'Payment complete for L1.' in page.get_by_role('status').inner_text()
                else:
                    page.wait_for_url('**/ui/fees/L1/')
                    assert page.get_by_role('heading', name='Late fee for L1').is_visible()
            finally:
                browser.close()

    assert requests == [('POST', '/charge?loan=L1', b'')]
