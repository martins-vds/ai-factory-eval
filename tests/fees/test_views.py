from datetime import date

import pytest
from playwright.sync_api import sync_playwright

from src.fees import views
from src.fees.services import GatewayResponse, PaymentApplication
from src.loans.repository import DjangoLoanRepository


class PaymentGateway:
    def __init__(self, response):
        self.response = response

    def charge(self, loan_id):
        return self.response


def use_test_gateway(response):
    return PaymentApplication(DjangoLoanRepository(), PaymentGateway(response))


@pytest.mark.django_db
def test_fee_api_matches_characterized_html(client):
    response = client.get('/fees/L3')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == (
        '<h1>Late fee for L3</h1><p>Due 2025-12-15, 19 day(s) late.</p>'
        '<p class="fee">Fee: $4.75</p>'
    )


@pytest.mark.django_db
def test_unknown_fee_api_returns_characterized_404(client):
    response = client.get('/fees/L9')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == '<p>No such loan.</p>'


@pytest.mark.django_db
def test_fee_api_formats_capped_amount(client, monkeypatch):
    monkeypatch.setattr(views.fee_application.clock, 'today', lambda: date(2026, 2, 25))

    response = client.get('/fees/L1')

    assert response.status_code == 200
    assert b'Fee: $10.00' in response.content


@pytest.mark.django_db
def test_unknown_fee_page_returns_404(client):
    response = client.get('/ui/fees/L9/')

    assert response.status_code == 404
    assert b'No such loan.' in response.content


@pytest.mark.django_db
def test_reading_room_fee_page_has_payment_action(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'Late fee for L3' in response.content
    assert b'19 day(s) late' in response.content
    assert b'Fee: $4.75' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content
    assert b'hx-on::before-swap' in response.content


@pytest.mark.django_db
def test_api_payment_preserves_success_response(client, monkeypatch):
    monkeypatch.setattr(
        views,
        'payment_application',
        use_test_gateway(GatewayResponse(200, b'charged\n')),
    )

    response = client.post('/payments/L3')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'charged\n'


@pytest.mark.django_db
def test_payment_api_uses_default_composition_for_unknown_loan(client):
    response = client.post('/payments/L9')

    assert response.status_code == 404
    assert response.content == b'no such loan\n'


@pytest.mark.django_db
def test_htmx_payment_success_renders_status(client, monkeypatch):
    monkeypatch.setattr(
        views,
        'payment_application',
        use_test_gateway(GatewayResponse(200, b'charged\n')),
    )

    response = client.post('/ui/payments/L3/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'<div role="status">charged' in response.content
    assert b'role="alert"' not in response.content


@pytest.mark.django_db
def test_htmx_payment_renders_escaped_gateway_failure(client, monkeypatch):
    monkeypatch.setattr(
        views,
        'payment_application',
        use_test_gateway(GatewayResponse(503, b'<script>bad()</script>')),
    )

    response = client.post('/ui/payments/L3/', HTTP_HX_REQUEST='true')

    assert response.status_code == 502
    assert b'<div role="alert">' in response.content
    assert b'&lt;script&gt;bad()&lt;/script&gt;' in response.content


@pytest.mark.django_db
def test_htmx_payment_replaces_invalid_gateway_bytes(client, monkeypatch):
    monkeypatch.setattr(
        views,
        'payment_application',
        use_test_gateway(GatewayResponse(503, b'\xff')),
    )

    response = client.post('/ui/payments/L3/', HTTP_HX_REQUEST='true')

    assert response.status_code == 502
    assert b'\xef\xbf\xbd' in response.content


@pytest.mark.django_db
@pytest.mark.parametrize('path', ['/fees/L3', '/ui/fees/L3/'])
def test_fee_views_require_get(client, path):
    assert client.post(path).status_code == 405


@pytest.mark.django_db
@pytest.mark.parametrize('path', ['/payments/L3', '/ui/payments/L3/'])
def test_payment_views_require_post(client, monkeypatch, path):
    monkeypatch.setattr(
        views,
        'payment_application',
        use_test_gateway(GatewayResponse(200, b'charged\n')),
    )

    assert client.get(path).status_code == 405


@pytest.mark.django_db
def test_browser_displays_htmx_payment_failure(live_server, monkeypatch):
    monkeypatch.setattr(
        views,
        'payment_application',
        use_test_gateway(GatewayResponse(502, b'payment gateway unavailable\n')),
    )

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/fees/L3/')
            page.get_by_role('button', name='Pay late fee').click()
            assert page.get_by_role('alert').inner_text().strip() == 'payment gateway unavailable'
        finally:
            browser.close()
