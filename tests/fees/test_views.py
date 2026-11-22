from datetime import date

import pytest
from playwright.sync_api import sync_playwright

from src.fees.composition import payment_application
from src.fees.services import PaymentGatewayInterrupted


@pytest.mark.django_db
def test_fee_endpoint_matches_characterized_html(client):
    response = client.get('/fees/L3')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == (
        '<h1>Late fee for L3</h1><p>Due 2025-12-15, 19 day(s) late.</p>'
        '<p class="fee">Fee: $4.75</p>'
    )


@pytest.mark.django_db
def test_fee_endpoint_returns_characterized_missing_loan_response(client):
    response = client.get('/fees/L9')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content == b'<p>No such loan.</p>'


@pytest.mark.django_db
def test_fee_page_shows_fee_and_htmx_payment_form(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'Late fee for L3' in response.content
    assert b'19 day(s) late' in response.content
    assert b'Fee: $4.75' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content
    assert b'htmx.config.responseHandling' in response.content


@pytest.mark.django_db
def test_fee_endpoint_formats_the_maximum_fee(client, monkeypatch):
    monkeypatch.setattr(
        'src.loans.clock.SystemClock.today',
        lambda clock: date(2026, 6, 30),
    )

    response = client.get('/fees/L1')

    assert response.status_code == 200
    assert b'165 day(s) late' in response.content
    assert b'Fee: $10.00' in response.content


@pytest.mark.django_db
def test_fee_page_returns_the_missing_loan_fragment(client):
    response = client.get('/ui/fees/L9/')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content == b'<p>No such loan.</p>'


@pytest.mark.django_db
def test_payment_endpoint_forwards_successful_gateway_response(client, payment_gateway_server):
    requests, _ = payment_gateway_server

    response = client.post('/payments/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'charged\n'
    assert requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_payment_endpoint_maps_gateway_failure_to_bad_gateway(client, payment_gateway_server):
    requests, reply = payment_gateway_server
    reply.update(status=503, body=b'declined\n')

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'declined\n'
    assert requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_payment_endpoint_does_not_call_gateway_for_unknown_loan(client, payment_gateway_server):
    requests, _ = payment_gateway_server

    response = client.post('/payments/L9')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'no such loan\n'
    assert requests == []


@pytest.mark.django_db
def test_htmx_payment_failure_renders_an_error_fragment(client, payment_gateway_server):
    _, reply = payment_gateway_server
    reply.update(status=503, body=b'declined\n')

    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 502
    assert b'id="payment-result"' in response.content
    assert b'role="alert"' in response.content
    assert b'declined' in response.content


@pytest.mark.django_db
def test_ui_payment_success_renders_a_status_fragment(client, payment_gateway_server):
    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'id="payment-result"' in response.content
    assert b'role="status"' in response.content
    assert b'charged' in response.content


@pytest.mark.django_db
def test_interrupted_payment_returns_gateway_failure_without_losing_cause(
    client, monkeypatch, caplog
):
    interruption = InterruptedError('request interrupted')

    def interrupt(loan_id):
        raise PaymentGatewayInterrupted('payment request interrupted') from interruption

    monkeypatch.setattr(payment_application.gateway, 'charge', interrupt)

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'
    gateway_error = next(
        record for record in caplog.records if record.name == 'src.fees.views' and record.exc_info
    )
    assert gateway_error.message == 'payment gateway request interrupted'
    assert gateway_error.exc_info[1].__cause__ is interruption


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('method', 'path'),
    [
        ('post', '/fees/L3'),
        ('post', '/ui/fees/L3/'),
        ('get', '/payments/L1'),
        ('get', '/ui/payments/L1/'),
    ],
)
def test_fee_and_payment_routes_reject_unsupported_methods(
    client, payment_gateway_server, method, path
):
    requests, _ = payment_gateway_server

    response = getattr(client, method)(path)

    assert response.status_code == 405
    assert requests == []


@pytest.mark.django_db
def test_real_browser_can_pay_a_late_fee(live_server, payment_gateway_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/fees/L1/')
            assert page.get_by_role('heading', name='Late fee for L1').count() == 1
            page.get_by_role('button', name='Pay late fee').click()
            page.get_by_role('status').wait_for()

            assert page.get_by_role('status').inner_text() == 'charged'
        finally:
            browser.close()


@pytest.mark.django_db
def test_real_browser_renders_a_payment_gateway_error(live_server, payment_gateway_server):
    _, reply = payment_gateway_server
    reply.update(status=503, body=b'declined\n')

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/fees/L1/')
            page.get_by_role('button', name='Pay late fee').click()
            page.get_by_role('alert').wait_for()

            assert page.get_by_role('alert').inner_text() == 'declined'
        finally:
            browser.close()
