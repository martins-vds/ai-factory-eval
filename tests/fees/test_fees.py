from datetime import date
from decimal import Decimal

import pytest

from src.fees.services import calculate_late_fee


def test_late_fee_charges_twenty_five_cents_per_day_after_grace_threshold():
    fee = calculate_late_fee(
        due_on=date(2026, 11, 12),
        returned_on=None,
        today=date(2026, 11, 15),
    )

    assert fee.days_late == 3
    assert fee.amount == Decimal('0.75')


def test_late_fee_matches_characterized_nineteen_day_amount():
    fee = calculate_late_fee(
        due_on=date(2025, 12, 15),
        returned_on=date(2026, 1, 3),
        today=date(2026, 11, 15),
    )

    assert fee.days_late == 19
    assert fee.amount == Decimal('4.75')


@pytest.mark.django_db
def test_fee_api_returns_characterized_html_for_a_known_loan(client):
    response = client.get('/fees/L3')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == (
        '<h1>Late fee for L3</h1><p>Due 2025-12-15, 19 day(s) late.</p>'
        '<p class="fee">Fee: $4.75</p>'
    )
