from datetime import date, timedelta
from decimal import Decimal

import pytest

from src.fees.services import calculate_late_fee


@pytest.mark.parametrize(
    ('days_late', 'expected_amount'),
    [
        (-3, Decimal('0.00')),
        (0, Decimal('0.00')),
        (1, Decimal('0.00')),
        (2, Decimal('0.00')),
        (3, Decimal('0.75')),
        (40, Decimal('10.00')),
        (100, Decimal('10.00')),
    ],
)
def test_late_fee_uses_two_day_grace_and_caps_at_ten_dollars(days_late, expected_amount):
    due_on = date(2026, 1, 1)

    fee = calculate_late_fee(due_on, due_on + timedelta(days=days_late))

    assert fee.days_late == max(0, days_late)
    assert fee.amount == expected_amount


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
def test_browser_fee_page_uses_reading_room_layout_and_offers_htmx_payment(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'A small nudge, never a surprise' in response.content
    assert b'Late fees' in response.content
    assert b'Due Dec 15, 2025' in response.content
    assert b'19 late days' in response.content
    assert b'first two days waived' in response.content
    assert b'$4.75' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content
    assert b'action="/ui/payments/L3/"' in response.content
