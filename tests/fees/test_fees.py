import json
from datetime import date, timedelta
from pathlib import Path

import pytest
from django.utils import timezone

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
