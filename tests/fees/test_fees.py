from datetime import timedelta

import pytest
from django.utils import timezone

from src.loans.models import Loan


@pytest.mark.django_db
def test_fee_endpoint_displays_characterized_days_and_amount(client):
    today = timezone.localdate()
    due_on = today - timedelta(days=19)
    Loan.objects.create(
        id='L9',
        member='reader',
        isbn='123',
        lent_on=due_on - timedelta(days=14),
    )

    response = client.get('/fees/L9')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == (
        f'<h1>Late fee for L9</h1><p>Due {due_on.isoformat()}, 19 day(s) late.</p>'
        '<p class="fee">Fee: $4.75</p>'
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('late_days', 'expected_amount'),
    [(0, '0.00'), (2, '0.00'), (3, '0.75'), (40, '10.00'), (41, '10.00')],
)
def test_fee_endpoint_applies_grace_period_and_cap(client, late_days, expected_amount):
    today = timezone.localdate()
    due_on = today - timedelta(days=late_days)
    loan_id = f'L{late_days + 10}'
    Loan.objects.create(
        id=loan_id,
        member='reader',
        isbn='123',
        lent_on=due_on - timedelta(days=14),
    )

    response = client.get(f'/fees/{loan_id}')

    assert response.status_code == 200
    assert f'Fee: ${expected_amount}' in response.content.decode()


@pytest.mark.django_db
def test_fee_endpoint_uses_return_date_instead_of_current_date(client):
    today = timezone.localdate()
    due_on = today - timedelta(days=19)
    Loan.objects.create(
        id='L9',
        member='reader',
        isbn='123',
        lent_on=due_on - timedelta(days=14),
        returned_on=due_on + timedelta(days=2),
    )

    response = client.get('/fees/L9')

    assert response.status_code == 200
    assert b'2 day(s) late' in response.content
    assert b'Fee: $0.00' in response.content


@pytest.mark.django_db
def test_fee_endpoint_returns_characterized_not_found_response(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == '<p>No such loan.</p>'


@pytest.mark.django_db
def test_reading_room_fee_page_shows_fee_and_htmx_payment_action(client):
    today = timezone.localdate()
    due_on = today - timedelta(days=19)
    Loan.objects.create(
        id='L9',
        member='reader',
        isbn='123',
        lent_on=due_on - timedelta(days=14),
    )

    response = client.get('/ui/fees/L9/')

    assert response.status_code == 200
    assert b'Late fee for L9</h1>' in response.content
    assert due_on.isoformat().encode() in response.content
    assert b'>19</dd>' in response.content
    assert b'Fee: $4.75' in response.content
    assert b'hx-post="/ui/payments/L9/"' in response.content
