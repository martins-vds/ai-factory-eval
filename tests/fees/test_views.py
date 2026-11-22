import pytest


pytestmark = pytest.mark.django_db


def test_fee_api_returns_the_characterized_html_fragment(client):
    response = client.get('/fees/L3')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == (
        '<h1>Late fee for L3</h1><p>Due 2025-12-15, 19 day(s) late.</p>'
        '<p class="fee">Fee: $4.75</p>'
    )


def test_fee_api_returns_the_characterized_not_found_response(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content == b'<p>No such loan.</p>'


def test_fee_ui_page_shows_late_fee_and_htmx_payment_action(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'Late fee for L3' in response.content
    assert b'2025-12-15' in response.content
    assert b'19 day(s)' in response.content
    assert b'$4.75' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content


def test_fee_ui_page_shows_not_found_for_unknown_loan(client):
    response = client.get('/ui/fees/unknown/')

    assert response.status_code == 404
    assert b'No such loan.' in response.content


def test_payment_api_forwards_gateway_success(client, gateway_server, monkeypatch):
    gateway_url, requests = gateway_server(200, b'charged\n')
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

    response = client.post('/payments/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'charged\n'
    assert requests == [('POST', '/charge?loan=L1', b'')]


def test_payment_api_maps_gateway_failure_to_bad_gateway(client, gateway_server, monkeypatch):
    gateway_url, _ = gateway_server(503, b'declined\n')
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

    response = client.post('/payments/L2')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'declined\n'


def test_payment_api_rejects_unknown_loan_without_calling_gateway(
    client,
    gateway_server,
    monkeypatch,
):
    gateway_url, requests = gateway_server(200, b'charged\n')
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

    response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'no such loan\n'
    assert requests == []


def test_payment_api_logs_interruption_and_returns_gateway_failure(
    client,
    monkeypatch,
    caplog,
):
    from src.fees.gateway import request

    def interrupt(*args, **kwargs):
        raise InterruptedError('request interrupted')

    monkeypatch.setattr(request, 'urlopen', interrupt)

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'
    assert 'request interrupted' in caplog.text


def test_fee_ui_payment_renders_success_fragment(client, gateway_server, monkeypatch):
    gateway_url, _ = gateway_server(200, b'charged\n')
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="status"' in response.content
    assert b'charged' in response.content


def test_fee_ui_payment_renders_gateway_failure_for_htmx(client, gateway_server, monkeypatch):
    gateway_url, _ = gateway_server(503, b'declined\n')
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="alert"' in response.content
    assert b'declined' in response.content


def test_fee_ui_payment_renders_a_full_page_without_htmx(client, gateway_server, monkeypatch):
    gateway_url, _ = gateway_server(200, b'charged\n')
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)

    response = client.post('/ui/payments/L1/')

    assert response.status_code == 200
    assert b'<!doctype html>' in response.content
    assert b'role="status"' in response.content
    assert b'charged' in response.content


def test_fee_ui_htmx_payment_renders_unknown_loan_error(client):
    response = client.post('/ui/payments/unknown/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="alert"' in response.content
    assert b'no such loan' in response.content


def test_fee_ui_payment_rejects_unsupported_methods(client):
    response = client.get('/ui/payments/L1/')

    assert response.status_code == 405
