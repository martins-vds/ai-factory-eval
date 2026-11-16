import json
import logging
from datetime import date, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest
from django.test import Client

from src.fees.services import calculate_late_fee

GOLDENS = Path(__file__).resolve().parents[2] / '.migration/characterization/source/goldens'
HTTP_GOLDENS = json.loads((GOLDENS / 'http.json').read_text(encoding='utf-8'))
EDGE_GOLDENS = json.loads((GOLDENS / 'edge-cases.json').read_text(encoding='utf-8'))


def test_late_fee_waives_two_days_and_charges_twenty_five_cents_from_day_three():
    due_on = date(2026, 1, 1)

    within_grace_period = calculate_late_fee(
        SimpleNamespace(due_on=due_on, returned_on=due_on + timedelta(days=2)),
        today=due_on + timedelta(days=2),
    )
    after_grace_period = calculate_late_fee(
        SimpleNamespace(due_on=due_on, returned_on=due_on + timedelta(days=3)),
        today=due_on + timedelta(days=3),
    )

    assert (within_grace_period.late_days, within_grace_period.amount_cents) == (2, 0)
    assert (after_grace_period.late_days, after_grace_period.amount_cents) == (3, 75)


def test_unreturned_loan_uses_today_and_early_return_has_no_late_days():
    due_on = date(2026, 1, 1)

    overdue = calculate_late_fee(
        SimpleNamespace(due_on=due_on, returned_on=None),
        today=due_on + timedelta(days=19),
    )
    early = calculate_late_fee(
        SimpleNamespace(due_on=due_on, returned_on=due_on - timedelta(days=1)),
        today=due_on + timedelta(days=19),
    )

    assert (overdue.late_days, overdue.amount_cents) == (19, 475)
    assert (early.late_days, early.amount_cents) == (0, 0)


def test_late_fee_is_capped_at_ten_dollars():
    due_on = date(2026, 1, 1)
    fee = calculate_late_fee(
        SimpleNamespace(due_on=due_on, returned_on=due_on + timedelta(days=100)),
        today=due_on + timedelta(days=100),
    )

    assert fee.amount_cents == 1000


@pytest.mark.django_db
def test_fee_api_matches_the_characterized_response(client):
    golden = HTTP_GOLDENS['GET /fees/{id}']

    response = client.get(golden['request']['path'])

    assert response.status_code == golden['response']['status']
    assert response['Content-Type'] == golden['response']['content_type']
    assert response.content.decode() == golden['response']['body']


@pytest.mark.django_db
def test_fee_api_returns_the_characterized_not_found_response(client):
    expected = EDGE_GOLDENS['GET /fees/unknown']['response']

    response = client.get('/fees/unknown')

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']


@pytest.mark.django_db
def test_fee_page_uses_the_reading_room_layout_and_ui_payment_path(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'Late fees</h1>' in response.content
    assert b'19 late days' in response.content
    assert b'$4.75' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content
    assert b'action="/ui/payments/L3/"' in response.content
    assert b'daisyui@4.12.24' in response.content
    assert b'htmx.org@2.0.11' in response.content


@pytest.mark.django_db
def test_payment_api_posts_to_the_gateway_and_forwards_success(
    client, monkeypatch, payment_gateway
):
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', payment_gateway.url)

    response = client.post('/payments/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'charged\n'
    assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_payment_api_maps_gateway_declines_to_bad_gateway(client, monkeypatch, payment_gateway):
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', payment_gateway.url)

    response = client.post('/payments/L2')

    assert response.status_code == 502
    assert response.content == b'declined\n'
    assert payment_gateway.requests == [('POST', '/charge?loan=L2', b'')]


@pytest.mark.django_db
def test_payment_api_maps_gateway_connection_failure_to_bad_gateway(client, monkeypatch):
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', 'http://127.0.0.1:1')

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'


@pytest.mark.django_db
def test_payment_for_unknown_loan_does_not_call_the_gateway(monkeypatch, payment_gateway):
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', payment_gateway.url)

    response = Client(enforce_csrf_checks=True).post('/payments/unknown')
    ui_response = Client(enforce_csrf_checks=True).post('/ui/payments/L1/')

    assert response.status_code == 404
    assert response.content == b'no such loan\n'
    assert ui_response.status_code == 403
    assert payment_gateway.requests == []


@pytest.mark.django_db
def test_interrupted_payment_returns_bad_gateway_without_losing_interrupt(
    client, monkeypatch, caplog
):
    def interrupt(*args, **kwargs):
        raise InterruptedError('request interrupted')

    monkeypatch.setattr('src.fees.gateway.urlopen', interrupt)
    with caplog.at_level(logging.ERROR, logger='src.fees.views'):
        response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'
    failure = next(record.exc_info[1] for record in caplog.records if record.exc_info)
    assert isinstance(failure.__cause__, InterruptedError)


@pytest.mark.django_db
def test_htmx_payment_action_uses_the_gateway_and_returns_status_fragment(
    client, monkeypatch, payment_gateway
):
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', payment_gateway.url)

    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="status"' in response.content
    assert b'Payment received for L1.' in response.content
    assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_htmx_payment_failure_displays_a_gateway_error(client, monkeypatch):
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', 'http://127.0.0.1:1')

    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="alert"' in response.content
    assert b'payment gateway unavailable' in response.content
