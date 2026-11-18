import logging
from datetime import date

import pytest

from src.fees.gateway import HttpPaymentGateway
from src.loans.models import Loan


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
    assert response.content.decode() == '<p>No such loan.</p>'


@pytest.mark.django_db
def test_fee_api_formats_the_capped_amount_as_ten_dollars(client):
    Loan.objects.create(
        id='L9',
        member='reader',
        isbn='123',
        lent_on=date(2026, 1, 1),
        returned_on=date(2026, 11, 18),
    )

    response = client.get('/fees/L9')

    assert response.status_code == 200
    assert 'Fee: $10.00' in response.content.decode()


@pytest.mark.django_db
def test_payment_api_gateway_forwards_success(client, payment_gateway_server):
    received, _, _ = payment_gateway_server

    response = client.post('/payments/L3')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'charged\n'
    assert received == [('POST', '/charge?loan=L3', b'')]


@pytest.mark.django_db
def test_payment_api_maps_decline_to_502_and_keeps_body(client, payment_gateway_server):
    received, configured_response, _ = payment_gateway_server
    configured_response.update(status=503, body=b'declined\n')

    response = client.post('/payments/L3')

    assert response.status_code == 502
    assert response.content.decode() == 'declined\n'
    assert received == [('POST', '/charge?loan=L3', b'')]


@pytest.mark.django_db
def test_payment_api_rejects_unknown_loan_without_gateway(client, payment_gateway_server):
    received, _, _ = payment_gateway_server

    response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response.content.decode() == 'no such loan\n'
    assert received == []


@pytest.mark.django_db
def test_payment_api_maps_an_interrupted_gateway_call_to_502(client, monkeypatch):
    def interrupt(gateway, loan_id):
        raise InterruptedError('request interrupted')

    monkeypatch.setattr(HttpPaymentGateway, 'charge', interrupt)

    response = client.post('/payments/L3')

    assert response.status_code == 502
    assert response.content.decode() == 'payment gateway unavailable\n'


@pytest.mark.django_db
def test_payment_api_maps_a_gateway_io_failure_to_502(client, monkeypatch):
    def fail(gateway, loan_id):
        raise OSError('connection failed')

    monkeypatch.setattr(HttpPaymentGateway, 'charge', fail)

    response = client.post('/payments/L3')

    assert response.status_code == 502
    assert response.content.decode() == 'payment gateway unavailable\n'


@pytest.mark.django_db
def test_payment_api_logs_interruption_and_returns_502(client, monkeypatch, caplog):
    def interrupt(gateway, loan_id):
        raise InterruptedError('request interrupted')

    monkeypatch.setattr(HttpPaymentGateway, 'charge', interrupt)

    with caplog.at_level(logging.WARNING, logger='src.fees.views'):
        response = client.post('/payments/L3')

    assert response.status_code == 502
    assert 'request interrupted' in caplog.text


@pytest.mark.django_db
def test_fee_page_uses_the_reading_room_layout_and_ui_payment_route(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'<!doctype html>' in response.content
    assert b'Late fee for loan L3' in response.content
    assert b'Fee: $4.75' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content
    assert b'hx-on::before-swap=' in response.content
    assert b'action="/ui/payments/L3/"' in response.content


@pytest.mark.django_db
def test_unknown_fee_page_renders_a_reading_room_not_found_page(client):
    response = client.get('/ui/fees/unknown/')

    assert response.status_code == 404
    assert b'<!doctype html>' in response.content
    assert b'Loan not found' in response.content


@pytest.mark.django_db
def test_htmx_payment_success_fragment(client, payment_gateway_server):
    response = client.post(
        '/ui/payments/L3/',
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert b'<!doctype html>' not in response.content
    assert b'role="status"' in response.content
    assert b'Payment received.' in response.content


@pytest.mark.django_db
def test_htmx_payment_gateway_failure_fragment(client, payment_gateway_server):
    _, configured_response, _ = payment_gateway_server
    configured_response.update(status=503, body=b'declined\n')

    response = client.post(
        '/ui/payments/L3/',
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert b'role="alert"' in response.content
    assert b'Payment could not be completed.' in response.content


@pytest.mark.django_db
def test_htmx_unknown_payment_shows_error_without_gateway(client, payment_gateway_server):
    received, _, _ = payment_gateway_server

    response = client.post(
        '/ui/payments/unknown/',
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert b'role="alert"' in response.content
    assert b'Loan not found.' in response.content
    assert received == []


@pytest.mark.django_db
def test_regular_payment_failure_renders_page(client, payment_gateway_server):
    _, configured_response, _ = payment_gateway_server
    configured_response.update(status=503, body=b'declined\n')

    response = client.post('/ui/payments/L3/')

    assert response.status_code == 502
    assert b'<!doctype html>' in response.content
    assert b'Fee: $4.75' in response.content
    assert b'role="alert"' in response.content


@pytest.mark.django_db
def test_regular_payment_success_redirects_to_the_fee_page(client, payment_gateway_server):
    response = client.post('/ui/payments/L3/')

    assert response.status_code == 302
    assert response['Location'] == '/ui/fees/L3/'


@pytest.mark.django_db
def test_regular_unknown_payment_renders_not_found(client, payment_gateway_server):
    received, _, _ = payment_gateway_server

    response = client.post('/ui/payments/unknown/')

    assert response.status_code == 404
    assert b'<!doctype html>' in response.content
    assert b'Loan not found' in response.content
    assert received == []


@pytest.mark.django_db
def test_routes_reject_unsupported_methods(client):
    assert client.post('/fees/L3').status_code == 405
    assert client.get('/payments/L3').status_code == 405
    assert client.post('/ui/fees/L3/').status_code == 405
    assert client.get('/ui/payments/L3/').status_code == 405
