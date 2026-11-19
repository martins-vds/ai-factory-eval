import pytest
from playwright.sync_api import sync_playwright

from src.fees import composition, gateway


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


@pytest.mark.django_db
def test_fee_api_returns_the_characterized_not_found_fragment(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
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
    assert response.content == b'no such loan\n'
    assert requests == []


@pytest.mark.django_db
def test_payment_api_turns_interruption_into_gateway_failure(client, monkeypatch):
    def interrupt(request):
        raise InterruptedError('request interrupted')

    monkeypatch.setattr(gateway, 'urlopen', interrupt)

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'


@pytest.mark.django_db
def test_fee_page_shows_the_quote_and_htmx_payment_action(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'Late fee for loan L3' in response.content
    assert b'19 day(s) late' in response.content
    assert b'$4.75' in response.content
    assert b'action="/ui/payments/L3/"' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content


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
