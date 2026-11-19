from datetime import date
from types import SimpleNamespace

import pytest
from playwright.sync_api import sync_playwright

from src.fees import composition, gateway, views


@pytest.mark.django_db
def test_fee_api_returns_the_characterized_html_fragment(client):
    response = client.get('/fees/L3')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == (
        '<h1>Late fee for L3</h1>'
        '<p>Due 2025-12-15, 19 day(s) late.</p>'
        '<p class="fee">Fee: $4.75</p>'
    )


def test_fee_api_formats_a_ten_dollar_fee_with_two_decimal_places(client, monkeypatch):
    quote = SimpleNamespace(
        loan=SimpleNamespace(id='L3', due_on=date(2025, 12, 15)),
        days_late=50,
        fee_cents=1000,
    )
    monkeypatch.setattr(
        views,
        'fee_application',
        SimpleNamespace(calculate_fee=lambda loan_id: quote),
    )

    response = client.get('/fees/L3')

    assert response.content.decode() == (
        '<h1>Late fee for L3</h1>'
        '<p>Due 2025-12-15, 50 day(s) late.</p>'
        '<p class="fee">Fee: $10.00</p>'
    )


@pytest.mark.django_db
def test_fee_api_returns_the_characterized_not_found_fragment(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content == b'<p>No such loan.</p>'


@pytest.mark.django_db
def test_fee_page_returns_the_not_found_fragment_for_an_unknown_loan(client):
    response = client.get('/ui/fees/unknown/')

    assert response.status_code == 404
    assert response['Content-Type'].startswith('text/html')
    assert response.content == b'<p>No such loan.</p>'


@pytest.mark.django_db
def test_payment_api_forwards_successful_gateway_response(client, gateway_server, monkeypatch):
    base_url, _, requests = gateway_server
    monkeypatch.setattr(composition.payment_application.gateway, 'base_url', base_url)

    response = client.post('/payments/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'charged\n'
    assert requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_payment_api_maps_non_success_gateway_response_to_bad_gateway(
    client, gateway_server, monkeypatch
):
    base_url, handler, requests = gateway_server
    handler.response_status = 503
    handler.response_body = b'declined\n'
    monkeypatch.setattr(composition.payment_application.gateway, 'base_url', base_url)

    response = client.post('/payments/L2')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'declined\n'
    assert requests == [('POST', '/charge?loan=L2', b'')]


@pytest.mark.django_db
def test_payment_api_rejects_unknown_loan_without_calling_gateway(
    client, gateway_server, monkeypatch
):
    base_url, _, requests = gateway_server
    monkeypatch.setattr(composition.payment_application.gateway, 'base_url', base_url)

    response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'no such loan\n'
    assert requests == []


@pytest.mark.django_db
def test_payment_api_turns_interruption_into_gateway_failure(client, monkeypatch):
    def interrupt(request):
        raise InterruptedError('request interrupted')

    monkeypatch.setattr(gateway, 'urlopen', interrupt)

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'payment gateway unavailable\n'


@pytest.mark.parametrize(
    ('method', 'path'),
    [
        ('post', '/fees/L3'),
        ('post', '/ui/fees/L3/'),
        ('get', '/payments/L1'),
        ('get', '/ui/payments/L1/'),
    ],
)
def test_fee_and_payment_routes_reject_unsupported_methods(client, monkeypatch, method, path):
    monkeypatch.setattr(
        views,
        'fee_application',
        SimpleNamespace(calculate_fee=lambda loan_id: None),
    )
    monkeypatch.setattr(
        views,
        'payment_application',
        SimpleNamespace(pay=lambda loan_id: None),
    )

    response = getattr(client, method)(path)

    assert response.status_code == 405


@pytest.mark.django_db
def test_fee_page_shows_the_quote_and_htmx_payment_action(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'A small nudge, never a surprise' in response.content
    assert b'Late fee for ISBN 9781617294945' in response.content
    assert b'19 day(s) late' in response.content
    assert b'$4.75' in response.content
    assert b'Fee: $4.75</p>' in response.content
    assert response.content.index(b'ISBN 9781617294945') < response.content.index(b'$4.75')
    assert b'action="/ui/payments/L3/"' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content


def test_fee_page_formats_a_ten_dollar_fee_with_two_decimal_places(client, monkeypatch):
    fee = SimpleNamespace(
        loan=SimpleNamespace(
            id='L3',
            isbn='9781617294945',
            member='cy',
            due_on=date(2025, 12, 15),
        ),
        days_late=50,
        fee_cents=1000,
    )
    monkeypatch.setattr(
        views,
        'fee_application',
        SimpleNamespace(calculate_fee=lambda loan_id: fee),
    )

    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'Fee: $10.00</p>' in response.content


@pytest.mark.django_db
def test_payment_page_renders_an_interruption_as_a_gateway_failure(client, monkeypatch):
    def interrupt(request):
        raise InterruptedError('request interrupted')

    monkeypatch.setattr(gateway, 'urlopen', interrupt)

    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 502
    assert response['Content-Type'].startswith('text/html')
    assert b'role="alert"' in response.content
    assert b'Payment failed: Payment gateway unavailable.' in response.content
    assert response.context['successful'] is False


@pytest.mark.django_db
def test_payment_page_renders_an_unknown_loan_as_not_found(client):
    response = client.post('/ui/payments/unknown/', HTTP_HX_REQUEST='true')

    assert response.status_code == 404
    assert response['Content-Type'].startswith('text/html')
    assert b'role="alert"' in response.content
    assert b'Payment failed: No such loan.' in response.content
    assert response.context['successful'] is False


@pytest.mark.django_db
def test_htmx_payment_displays_gateway_failures(client, gateway_server, monkeypatch):
    base_url, handler, requests = gateway_server
    handler.response_status = 503
    handler.response_body = b'declined\n'
    monkeypatch.setattr(composition.payment_application.gateway, 'base_url', base_url)

    response = client.post('/ui/payments/L2/', HTTP_HX_REQUEST='true')

    assert response.status_code == 502
    assert b'id="payment-status"' in response.content
    assert b'role="alert"' in response.content
    assert b'declined' in response.content
    assert requests == [('POST', '/charge?loan=L2', b'')]


@pytest.mark.django_db
def test_htmx_payment_displays_successful_gateway_response(client, gateway_server, monkeypatch):
    base_url, _, requests = gateway_server
    monkeypatch.setattr(composition.payment_application.gateway, 'base_url', base_url)

    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'id="payment-status"' in response.content
    assert b'role="status"' in response.content
    assert b'charged' in response.content
    assert requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_browser_displays_payment_gateway_failure(live_server, gateway_server, monkeypatch):
    base_url, handler, requests = gateway_server
    handler.response_status = 503
    handler.response_body = b'declined\n'
    monkeypatch.setattr(composition.payment_application.gateway, 'base_url', base_url)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/fees/L3/')
            page.get_by_role('button', name='Pay late fee').click()
            alert = page.get_by_role('alert')
            alert.wait_for()
            assert 'declined' in alert.inner_text()
            assert requests == [('POST', '/charge?loan=L3', b'')]
        finally:
            browser.close()
