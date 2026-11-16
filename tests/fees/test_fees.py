import json
from datetime import date
from pathlib import Path

import pytest

from src.loans.models import Loan
from src.fees.services import calculate_late_fee

HTTP_GOLDEN_PATH = (
    Path(__file__).resolve().parents[2] / '.migration/characterization/source/goldens/http.json'
)
HTTP_GOLDENS = json.loads(HTTP_GOLDEN_PATH.read_text(encoding='utf-8'))
EDGE_GOLDEN_PATH = (
    Path(__file__).resolve().parents[2]
    / '.migration/characterization/source/goldens/edge-cases.json'
)
EDGE_GOLDENS = json.loads(EDGE_GOLDEN_PATH.read_text(encoding='utf-8'))


@pytest.mark.django_db
def test_fee_api_matches_characterized_page(client):
    golden = HTTP_GOLDENS['GET /fees/{id}']

    response = client.get(golden['request']['path'])

    assert response.status_code == golden['response']['status']
    assert response['Content-Type'] == golden['response']['content_type']
    assert response.content.decode() == golden['response']['body']


@pytest.mark.parametrize(
    ('as_of', 'days_late', 'amount_cents'),
    [
        (date(2026, 1, 14), 0, 0),
        (date(2026, 1, 16), 1, 0),
        (date(2026, 1, 17), 2, 0),
        (date(2026, 1, 18), 3, 75),
        (date(2026, 3, 6), 50, 1000),
    ],
)
def test_fee_calculation_applies_grace_period_and_cap(as_of, days_late, amount_cents):
    loan = Loan(id='L9', member='reader', isbn='123', lent_on=date(2026, 1, 1))

    fee = calculate_late_fee(loan, as_of=as_of)

    assert fee.days_late == days_late
    assert fee.amount_cents == amount_cents


@pytest.mark.django_db
def test_fee_api_returns_characterized_not_found_for_unknown_loan(client):
    golden = EDGE_GOLDENS['GET /fees/unknown']['response']

    response = client.get('/fees/unknown')

    assert response.status_code == golden['status']
    assert response['Content-Type'] == golden['content_type']
    assert response.content.decode() == golden['body']
