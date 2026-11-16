from datetime import timedelta

import pytest
from django.utils import timezone

from src.loans.models import Loan


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
@pytest.mark.parametrize(
    ('days_late', 'expected_fee'),
    [(0, '$0.00'), (2, '$0.00'), (3, '$0.75'), (50, '$10.00')],
)
def test_fee_endpoint_applies_grace_period_and_cap(client, days_late, expected_fee):
    today = timezone.localdate()
    Loan.objects.create(
        id='L9',
        member='reader',
        isbn='123',
        lent_on=today - timedelta(days=14 + days_late),
    )

    response = client.get('/fees/L9')

    assert response.status_code == 200
    assert f'Fee: {expected_fee}'.encode() in response.content


@pytest.mark.django_db
def test_fee_endpoint_returns_the_characterized_not_found_fragment(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content == b'<p>No such loan.</p>'


@pytest.mark.django_db
def test_fee_page_shows_calculation_and_htmx_payment_action(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'Late fee for loan L3' in response.content
    assert b'2025-12-15' in response.content
    assert b'19 days late' in response.content
    assert b'$4.75' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content
