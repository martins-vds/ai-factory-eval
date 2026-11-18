from urllib.error import URLError

import pytest
from playwright.sync_api import sync_playwright


@pytest.mark.django_db
def test_fee_endpoint_matches_the_characterized_html(client):
    response = client.get('/fees/L3')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == (
        '<h1>Late fee for L3</h1><p>Due 2025-12-15, 19 day(s) late.</p>'
        '<p class="fee">Fee: $4.75</p>'
    )


@pytest.mark.django_db
def test_fee_endpoint_returns_the_characterized_not_found_response(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content == b'<p>No such loan.</p>'


@pytest.mark.django_db
def test_payment_endpoint_posts_to_the_gateway_and_returns_its_success(client, payment_gateway):
    response = client.post('/payments/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'charged\n'
    assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_payment_endpoint_maps_gateway_decline_to_502_and_preserves_its_body(
    client,
    payment_gateway,
):
    payment_gateway.response_status = 503
    payment_gateway.response_body = b'declined\n'

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'declined\n'


@pytest.mark.django_db
def test_payment_endpoint_does_not_call_gateway_for_an_unknown_loan(client, payment_gateway):
    response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response.content == b'no such loan\n'
    assert payment_gateway.requests == []


@pytest.mark.django_db
def test_payment_endpoint_reports_interruption_as_gateway_failure_without_losing_it(
    client,
    caplog,
    monkeypatch,
):
    def interrupt(*args, **kwargs):
        raise InterruptedError('request cancelled')

    monkeypatch.setattr('src.fees.gateway.urlopen', interrupt)

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'
    assert 'InterruptedError: request cancelled' in caplog.text


@pytest.mark.django_db
def test_payment_endpoint_maps_connection_error_to_gateway_unavailable(client, monkeypatch):
    def fail(*args, **kwargs):
        raise URLError('connection refused')

    monkeypatch.setattr('src.fees.gateway.urlopen', fail)

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'


@pytest.mark.django_db
def test_fee_page_uses_reading_room_layout_and_posts_payment_to_ui_route(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'Late fees</h1>' in response.content
    assert b'Fee due' in response.content
    assert b'$4.75' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content
    assert b'bg-[#f5f0e5]' in response.content


@pytest.mark.django_db
def test_fee_page_returns_not_found_for_an_unknown_loan(client):
    response = client.get('/ui/fees/unknown/')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content == b'<p>No such loan.</p>'


@pytest.mark.django_db
def test_htmx_payment_action_shows_gateway_success(client, payment_gateway):
    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'id="payment-status"' in response.content
    assert b'role="status"' in response.content
    assert b'charged' in response.content


@pytest.mark.django_db
def test_htmx_payment_action_shows_a_decline_without_losing_fee_page(client, payment_gateway):
    payment_gateway.response_status = 503
    payment_gateway.response_body = b'declined\n'

    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'id="payment-status"' in response.content
    assert b'role="alert"' in response.content
    assert b'declined' in response.content


@pytest.mark.django_db
def test_browser_can_view_and_pay_a_late_fee(live_server, payment_gateway):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/fees/L3/')
            assert page.get_by_role('heading', name='Late fees').is_visible()
            page.get_by_role('button', name='Pay late fee').click()
            status = page.get_by_role('status')
            status.wait_for()
            assert 'Payment received: charged' in status.inner_text()
        finally:
            browser.close()

    assert payment_gateway.requests == [('POST', '/charge?loan=L3', b'')]
