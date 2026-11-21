from datetime import date

import pytest
from playwright.sync_api import sync_playwright

from src.loans.models import Loan


@pytest.mark.django_db
def test_fee_api_returns_the_characterized_html(client):
    Loan.objects.create(
        id='L9',
        member='reader',
        isbn='123',
        lent_on=date(2025, 12, 1),
        returned_on=date(2026, 1, 3),
    )

    response = client.get('/fees/L9')

    assert response.status_code == 200
    assert response['Content-Type'].split(';', 1)[0] == 'text/html'
    assert response.content.decode() == (
        '<h1>Late fee for L9</h1><p>Due 2025-12-15, 19 day(s) late.</p>'
        '<p class="fee">Fee: $4.75</p>'
    )


@pytest.mark.django_db
def test_fee_api_returns_characterized_not_found_response(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response['Content-Type'].split(';', 1)[0] == 'text/html'
    assert response.content == b'<p>No such loan.</p>'


@pytest.mark.django_db
def test_payment_api_sends_the_gateway_request_and_returns_success(client, payment_gateway):
    response = client.post('/payments/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'charged\n'
    assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_payment_api_maps_gateway_declines_to_bad_gateway(client, payment_gateway):
    payment_gateway.response_status = 503
    payment_gateway.response_body = b'declined\n'

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'declined\n'


@pytest.mark.django_db
def test_payment_api_does_not_call_gateway_for_an_unknown_loan(client, payment_gateway):
    response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'no such loan\n'
    assert payment_gateway.requests == []


@pytest.mark.django_db
def test_payment_api_maps_gateway_connection_failures_to_bad_gateway(client, monkeypatch, caplog):
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', 'http://127.0.0.1:1')

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'
    assert 'Payment gateway request failed' in caplog.text
    assert 'ConnectionRefusedError' in caplog.text


@pytest.mark.django_db
def test_fee_page_shows_the_fee_and_payment_action(client):
    Loan.objects.create(
        id='L9',
        member='reader',
        isbn='123',
        lent_on=date(2025, 12, 1),
        returned_on=date(2026, 1, 3),
    )

    response = client.get('/ui/fees/L9/')

    assert response.status_code == 200
    assert b'The Lending Library' in response.content
    assert b'Late fee for L9' in response.content
    assert b'19' in response.content
    assert b'$4.75' in response.content
    assert b'hx-post="/ui/payments/L9/"' in response.content
    assert b'htmx:beforeSwap' in response.content


@pytest.mark.django_db
def test_fee_page_renders_an_error_for_an_unknown_loan(client):
    response = client.get('/ui/fees/unknown/')

    assert response.status_code == 404
    assert b'role="alert"' in response.content
    assert b'No such loan.' in response.content


@pytest.mark.django_db
def test_htmx_payment_success_updates_the_payment_panel(client, payment_gateway):
    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="status"' in response.content
    assert b'charged' in response.content
    assert b'<!doctype html>' not in response.content
    assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_htmx_payment_failure_renders_an_error_panel(client, payment_gateway):
    payment_gateway.response_status = 503
    payment_gateway.response_body = b'declined <script>alert(1)</script>\n'

    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 502
    assert b'role="alert"' in response.content
    assert b'declined' in response.content
    assert b'&lt;script&gt;' in response.content
    assert b'<script>' not in response.content
    assert b'hx-post="/ui/payments/L1/"' in response.content


@pytest.mark.django_db
def test_htmx_payment_for_unknown_loan_renders_an_error_panel(client, payment_gateway):
    response = client.post('/ui/payments/unknown/', HTTP_HX_REQUEST='true')

    assert response.status_code == 404
    assert b'role="alert"' in response.content
    assert b'No such loan.' in response.content
    assert b'<!doctype html>' not in response.content
    assert payment_gateway.requests == []


@pytest.mark.django_db
def test_standard_payment_failure_renders_an_error_page(client, payment_gateway):
    payment_gateway.response_status = 503
    payment_gateway.response_body = b'declined\n'

    response = client.post('/ui/payments/L1/')

    assert response.status_code == 502
    assert b'<!doctype html>' in response.content
    assert b'role="alert"' in response.content
    assert b'declined' in response.content
    assert b'action="/ui/payments/L1/"' in response.content


@pytest.mark.django_db
def test_standard_payment_for_an_unknown_loan_renders_an_error_page(client):
    response = client.post('/ui/payments/unknown/')

    assert response.status_code == 404
    assert b'<!doctype html>' in response.content
    assert b'role="alert"' in response.content
    assert b'No such loan.' in response.content


@pytest.mark.django_db
def test_standard_payment_connection_failure_is_logged_and_rendered(client, monkeypatch, caplog):
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', 'http://127.0.0.1:1')

    response = client.post('/ui/payments/L1/')

    assert response.status_code == 502
    assert b'payment gateway unavailable' in response.content
    assert 'Payment gateway request failed' in caplog.text
    assert 'ConnectionRefusedError' in caplog.text


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('path', 'method'),
    [
        ('/fees/L1', 'post'),
        ('/ui/fees/L1/', 'post'),
        ('/payments/L1', 'get'),
        ('/ui/payments/L1/', 'get'),
    ],
)
def test_fee_and_payment_routes_reject_unsupported_methods(client, payment_gateway, path, method):
    response = getattr(client, method)(path)

    assert response.status_code == 405
    assert payment_gateway.requests == []


@pytest.mark.django_db
def test_browser_can_view_fee_and_render_payment_failure(live_server, payment_gateway):
    payment_gateway.response_status = 503
    payment_gateway.response_body = b'declined\n'

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/fees/L1/')
            page.get_by_role('heading', name='Late fee for L1').wait_for()
            page.get_by_role('button', name='Pay fee').click()
            alert = page.get_by_role('alert')
            alert.wait_for()
            assert 'declined' in alert.inner_text()
        finally:
            browser.close()
