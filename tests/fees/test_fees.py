from datetime import date

import pytest

from src.loans.models import Loan


@pytest.mark.django_db
def test_fee_endpoint_charges_twenty_five_cents_after_two_day_grace_period(client):
    Loan.objects.create(
        id='F1',
        member='reader',
        isbn='123',
        lent_on=date(2025, 12, 18),
        returned_on=date(2026, 1, 4),
    )

    response = client.get('/fees/F1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html; charset=utf-8'
    assert response.content.decode() == (
        '<h1>Late fee for F1</h1><p>Due 2026-01-01, 3 day(s) late.</p>'
        '<p class="fee">Fee: $0.25</p>'
    )
