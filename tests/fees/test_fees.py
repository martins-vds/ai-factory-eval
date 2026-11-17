import json
import logging
from datetime import date, timedelta
from pathlib import Path

import pytest
from django.test import Client
from django.utils import timezone
from playwright.sync_api import sync_playwright

from src.fees.services import calculate_late_fee

GOLDENS = Path(__file__).resolve().parents[2] / '.migration/characterization/source/goldens'
HTTP_GOLDENS = json.loads((GOLDENS / 'http.json').read_text(encoding='utf-8'))
EDGE_GOLDENS = json.loads((GOLDENS / 'edge-cases.json').read_text(encoding='utf-8'))


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('loan_id', 'golden'),
    [
        ('L2', EDGE_GOLDENS['GET /fees/L2 early return']),
        ('L3', HTTP_GOLDENS['GET /fees/{id}']),
    ],
)
def test_fee_endpoint_matches_characterized_html(client, loan_id, golden):
    expected = golden['response']

    response = client.get(f'/fees/{loan_id}')

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']


@pytest.mark.django_db
def test_unreturned_loan_fee_uses_the_current_date(client):
    late_days = max(0, (timezone.localdate() - date(2026, 1, 16)).days)

    response = client.get('/fees/L1')

    assert response.status_code == 200
    assert response.content.decode() == (
        '<h1>Late fee for L1</h1>'
        f'<p>Due 2026-01-16, {late_days} day(s) late.</p>'
        '<p class="fee">Fee: $10.00</p>'
    )


@pytest.mark.django_db
def test_fee_endpoint_matches_characterized_missing_loan_response(client):
    expected = EDGE_GOLDENS['GET /fees/unknown']['response']

    response = client.get('/fees/unknown')

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']


@pytest.mark.parametrize(
    ('late_days', 'expected_cents'),
    [
        (-1, 0),
        (0, 0),
        (1, 0),
        (2, 0),
        (3, 75),
        (40, 1000),
        (296, 1000),
    ],
)
def test_late_fee_calculation_applies_waiver_and_cap(late_days, expected_cents):
    due_on = date(2026, 1, 16)
    loan = type('LoanRecord', (), {'due_on': due_on, 'returned_on': None})()

    fee = calculate_late_fee(loan, due_on + timedelta(days=late_days))

    assert fee.late_days == max(0, late_days)
    assert fee.amount_cents == expected_cents


def test_late_fee_calculation_uses_return_date_instead_of_today():
    due_on = date(2026, 1, 16)
    loan = type('LoanRecord', (), {'due_on': due_on, 'returned_on': date(2026, 1, 20)})()

    fee = calculate_late_fee(loan, date(2026, 5, 1))

    assert fee.late_days == 4
    assert fee.amount_cents == 100


@pytest.mark.django_db
def test_fee_page_uses_reading_room_layout_and_payment_action(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'The Lending Library' in response.content
    assert b'Late fees' in response.content
    assert b'cy \xc2\xb7 L3' in response.content
    assert b'19 late days' in response.content
    assert b'$4.75' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content


@pytest.mark.django_db
def test_fee_page_returns_not_found_for_unknown_loan(client):
    response = client.get('/ui/fees/unknown/')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content == b'<p>No such loan.</p>'


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('gateway_status', 'gateway_body', 'expected_status', 'expected_body'),
    [
        (200, b'charged\n', 200, b'charged\n'),
        (503, b'declined\n', 502, b'declined\n'),
        (302, b'redirected\n', 502, b'redirected\n'),
    ],
)
def test_payment_endpoint_preserves_gateway_contract(
    client,
    payment_gateway,
    gateway_status,
    gateway_body,
    expected_status,
    expected_body,
):
    payment_gateway.status = gateway_status
    payment_gateway.body = gateway_body

    response = client.post('/payments/L1')

    assert response.status_code == expected_status
    assert response['Content-Type'] == 'text/plain'
    assert response.content == expected_body
    assert payment_gateway.requests == [('POST', '/charge?loan=L1', '')]


@pytest.mark.django_db
def test_payment_api_accepts_characterized_post_without_browser_csrf_token(payment_gateway):
    response = Client(enforce_csrf_checks=True).post('/payments/L1')

    assert response.status_code == 200
    assert response.content == b'charged\n'
    assert payment_gateway.requests == [('POST', '/charge?loan=L1', '')]


@pytest.mark.django_db
def test_browser_payment_action_keeps_csrf_protection(payment_gateway):
    response = Client(enforce_csrf_checks=True).post('/ui/payments/L3/')

    assert response.status_code == 403
    assert payment_gateway.requests == []


@pytest.mark.django_db
def test_payment_endpoint_does_not_call_gateway_for_unknown_loan(client, payment_gateway):
    response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'no such loan\n'
    assert payment_gateway.requests == []


@pytest.mark.django_db
def test_payment_endpoint_maps_connection_failure_to_gateway_failure(client, payment_gateway):
    payment_gateway.stop()

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'payment gateway unavailable\n'


@pytest.mark.django_db
def test_payment_endpoint_logs_interruption_while_returning_gateway_failure(
    client,
    payment_gateway,
    monkeypatch,
    caplog,
):
    class InterruptedOpener:
        def open(self, _request):
            raise InterruptedError('gateway interrupted')

    monkeypatch.setattr('src.fees.gateway.build_opener', lambda *_args: InterruptedOpener())
    caplog.set_level(logging.ERROR, logger='src.fees.views')

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'
    assert 'InterruptedError: gateway interrupted' in caplog.text


@pytest.mark.django_db
def test_fee_payment_action_renders_gateway_failure_for_htmx(client, payment_gateway):
    payment_gateway.status = 503
    payment_gateway.body = b'declined\n'

    response = client.post('/ui/payments/L3/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="alert"' in response.content
    assert b'Payment could not be completed: declined' in response.content
    assert payment_gateway.requests == [('POST', '/charge?loan=L3', '')]


@pytest.mark.django_db
@pytest.mark.usefixtures('restore_seed_loans')
def test_real_browser_can_pay_a_late_fee(live_server, payment_gateway):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/fees/L3/')
            page.get_by_role('button', name='Pay $4.75 late fee').click()
            result = page.locator('#payment-result [role="status"]')
            result.wait_for()

            assert result.inner_text() == 'Payment received: charged'
            assert payment_gateway.requests == [('POST', '/charge?loan=L3', '')]
        finally:
            browser.close()
