import json
from datetime import date, timedelta
from pathlib import Path

import pytest

from src.loans.models import Loan

HTTP_GOLDEN_PATH = (
    Path(__file__).resolve().parents[2] / '.migration/characterization/source/goldens/http.json'
)
HTTP_GOLDENS = json.loads(HTTP_GOLDEN_PATH.read_text(encoding='utf-8'))


@pytest.mark.django_db
def test_fee_api_matches_the_characterized_page_for_an_existing_loan(client):
    golden = HTTP_GOLDENS['GET /fees/{id}']

    response = client.get(golden['request']['path'])

    assert response.status_code == golden['response']['status']
    assert response['Content-Type'] == golden['response']['content_type']
    assert response.content.decode() == golden['response']['body']


@pytest.mark.django_db
@pytest.mark.parametrize(('days_late', 'amount'), [(2, '0.00'), (3, '0.75')])
def test_fee_api_waives_only_two_days_and_charges_all_late_days_after(
    client, days_late, amount
):
    loan = Loan.objects.create(
        id=f'F{days_late}',
        member='reader',
        isbn='123',
        lent_on=date(2026, 1, 1),
        returned_on=date(2026, 1, 15) + timedelta(days=days_late),
    )

    response = client.get(f'/fees/{loan.id}')

    assert response.status_code == 200
    assert response.content.decode() == (
        f'<h1>Late fee for {loan.id}</h1>'
        f'<p>Due 2026-01-15, {days_late} day(s) late.</p>'
        f'<p class="fee">Fee: ${amount}</p>'
    )
