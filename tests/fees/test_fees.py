from datetime import date, timedelta

import pytest
from django.utils import timezone

from src.loans.models import Loan


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('late_days', 'expected_fee'),
    [
        (0, '$0.00'),
        (1, '$0.00'),
        (2, '$0.00'),
        (3, '$0.25'),
        (40, '$9.50'),
        (42, '$10.00'),
        (100, '$10.00'),
    ],
)
def test_fee_endpoint_applies_grace_period_daily_rate_and_cap(
    client, monkeypatch, late_days, expected_fee
):
    today = date(2026, 11, 15)
    monkeypatch.setattr(timezone, 'localdate', lambda: today)
    due_on = today - timedelta(days=late_days)
    loan = Loan.objects.create(
        id='L9',
        member='reader',
        isbn='123',
        lent_on=due_on - timedelta(days=14),
    )

    response = client.get(f'/fees/{loan.id}')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html'
    assert f'Due {due_on.isoformat()}, {late_days} day(s) late.'.encode() in response.content
    assert f'Fee: {expected_fee}'.encode() in response.content


@pytest.mark.django_db
def test_fee_for_returned_loan_uses_return_date_instead_of_today(client, monkeypatch):
    today = date(2026, 11, 15)
    monkeypatch.setattr(timezone, 'localdate', lambda: today)
    due_on = date(2026, 1, 1)
    Loan.objects.create(
        id='L9',
        member='reader',
        isbn='123',
        lent_on=due_on - timedelta(days=14),
        returned_on=due_on + timedelta(days=3),
    )

    response = client.get('/fees/L9')

    assert response.status_code == 200
    assert f'Due {due_on.isoformat()}, 3 day(s) late.'.encode() in response.content
    assert b'Fee: $0.25' in response.content


@pytest.mark.django_db
def test_fee_endpoint_returns_characterized_not_found_response(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content == b'<p>No such loan.</p>'


@pytest.mark.django_db
def test_reading_room_fee_page_has_htmx_payment_action(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'<!doctype html>' in response.content
    assert b'Late fees' in response.content
    assert b'Loan L3' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content
    assert b'class="card' in response.content
