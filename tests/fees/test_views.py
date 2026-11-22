import json
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

HTTP_GOLDENS = json.loads(
    (
        Path(__file__).resolve().parents[2] / '.migration/characterization/source/goldens/http.json'
    ).read_text(encoding='utf-8')
)


@pytest.mark.django_db
def test_fee_api_matches_characterized_response(client):
    expected = HTTP_GOLDENS['GET /fees/{id}']['response']

    response = client.get('/fees/L3')

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']


@pytest.mark.django_db
def test_fee_api_returns_characterized_not_found_response(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == '<p>No such loan.</p>'


@pytest.mark.django_db
def test_payment_api_posts_to_gateway_and_returns_success_body(
    client, payment_server, monkeypatch
):
    monkeypatch.setenv(
        'PAYMENT_GATEWAY_URL',
        f'http://127.0.0.1:{payment_server.server_port}',
    )

    response = client.post('/payments/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'charged\n'
    assert payment_server.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_payment_api_returns_gateway_failure_body_as_502(client, payment_server, monkeypatch):
    payment_server.response_status = 503
    payment_server.response_body = b'declined\n'
    monkeypatch.setenv(
        'PAYMENT_GATEWAY_URL',
        f'http://127.0.0.1:{payment_server.server_port}',
    )

    response = client.post('/payments/L2')

    assert response.status_code == 502
    assert response.content == b'declined\n'


@pytest.mark.django_db
def test_payment_api_does_not_call_gateway_for_unknown_loan(
    client, payment_server, monkeypatch
):
    monkeypatch.setenv(
        'PAYMENT_GATEWAY_URL',
        f'http://127.0.0.1:{payment_server.server_port}',
    )

    response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response.content == b'no such loan\n'
    assert payment_server.requests == []


@pytest.mark.django_db
def test_fee_page_has_reading_room_layout_and_payment_action(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'>Late fee for L3</h1>' in response.content
    assert b'Due Dec 15, 2025, 19 day(s) late.' in response.content
    assert b'Fee: $4.75' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content
    assert b'htmx:beforeSwap' in response.content


@pytest.mark.django_db
def test_fee_page_returns_not_found_for_unknown_loan(client):
    response = client.get('/ui/fees/unknown/')

    assert response.status_code == 404
    assert b'No such loan.' in response.content


@pytest.mark.django_db
def test_htmx_payment_page_renders_success_and_failure_responses(
    client, payment_server, monkeypatch
):
    monkeypatch.setenv(
        'PAYMENT_GATEWAY_URL',
        f'http://127.0.0.1:{payment_server.server_port}',
    )
    success = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')
    payment_server.response_status = 503
    payment_server.response_body = b'declined\n'
    failure = client.post('/ui/payments/L2/', HTTP_HX_REQUEST='true')

    assert success.status_code == 200
    assert b'role="status"' in success.content
    assert b'charged' in success.content
    assert failure.status_code == 502
    assert b'role="alert"' in failure.content
    assert b'declined' in failure.content


@pytest.mark.django_db
def test_regular_payment_redirects_to_the_local_fee_page(client, payment_server, monkeypatch):
    monkeypatch.setenv(
        'PAYMENT_GATEWAY_URL',
        f'http://127.0.0.1:{payment_server.server_port}',
    )

    response = client.post('/ui/payments/L1/')

    assert response.status_code == 302
    assert response['Location'] == '/ui/fees/L1/'


@pytest.mark.django_db
def test_browser_renders_htmx_gateway_failure(live_server, payment_server, monkeypatch):
    payment_server.response_status = 503
    payment_server.response_body = b'declined\n'
    monkeypatch.setenv(
        'PAYMENT_GATEWAY_URL',
        f'http://127.0.0.1:{payment_server.server_port}',
    )

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/fees/L3/')
            assert page.evaluate("typeof window.htmx !== 'undefined'")

            page.get_by_role('button', name='Pay late fee').click()
            page.locator('#payment-status [role="alert"]').wait_for()

            assert 'Payment failed: declined' in page.locator('#payment-status').inner_text()
        finally:
            browser.close()
