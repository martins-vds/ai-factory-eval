from datetime import date

import pytest

from src.loans.models import Loan


@pytest.mark.django_db
def test_fee_api_matches_characterized_html_fragment(client):
    Loan.objects.create(
        id='L-test',
        member='dee',
        isbn='123',
        lent_on=date(2025, 12, 1),
        returned_on=date(2026, 1, 3),
    )

    response = client.get('/fees/L-test')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html; charset=utf-8'
    assert response.content.decode() == (
        '<h1>Late fee for L-test</h1><p>Due 2025-12-15, 19 day(s) late.</p>'
        '<p class="fee">Fee: $4.75</p>'
    )


def test_missing_fee_api_response_matches_characterization(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response.content.decode() == '<p>No such loan.</p>'


@pytest.mark.django_db
def test_payment_api_forwards_gateway_request_and_success(client, monkeypatch, payment_gateway):
    Loan.objects.create(
        id='L-pay',
        member='dee',
        isbn='123',
        lent_on=date(2026, 11, 1),
    )
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', payment_gateway.url)

    response = client.post('/payments/L-pay')

    assert response.status_code == 200
    assert response.content == b'charged\n'
    assert payment_gateway.requests == [('POST', '/charge?loan=L-pay', b'')]


@pytest.mark.django_db
def test_non_200_gateway_response_becomes_502_with_gateway_body(
    client, monkeypatch, payment_gateway
):
    Loan.objects.create(
        id='L-pay',
        member='dee',
        isbn='123',
        lent_on=date(2026, 11, 1),
    )
    payment_gateway.status = 503
    payment_gateway.body = b'declined\n'
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', payment_gateway.url)

    response = client.post('/payments/L-pay')

    assert response.status_code == 502
    assert response.content == b'declined\n'
    assert payment_gateway.requests == [('POST', '/charge?loan=L-pay', b'')]


def test_payment_api_unknown_loan_does_not_call_gateway(
    client, monkeypatch, payment_gateway
):
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', payment_gateway.url)

    response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response.content == b'no such loan\n'
    assert payment_gateway.requests == []


@pytest.mark.django_db
def test_fee_page_has_payment_action_and_htmx_failure_is_renderable(
    client, monkeypatch, payment_gateway
):
    Loan.objects.create(
        id='L-ui',
        member='dee',
        isbn='123',
        lent_on=date(2025, 12, 1),
        returned_on=date(2026, 1, 3),
    )
    response = client.get('/ui/fees/L-ui/')

    assert response.status_code == 200
    assert b'Fee: $4.75' in response.content
    assert b'hx-post="/ui/payments/L-ui/"' in response.content
    assert b'/ui/payments/L-ui/' in response.content

    payment_gateway.status = 503
    payment_gateway.body = b'declined\n'
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', payment_gateway.url)
    payment_response = client.post(
        '/ui/payments/L-ui/',
        HTTP_HX_REQUEST='true',
        HTTP_REFERER='/ui/fees/L-ui/',
    )

    assert payment_response.status_code == 502
    assert b'role="alert"' in payment_response.content
    assert b'declined' in payment_response.content
