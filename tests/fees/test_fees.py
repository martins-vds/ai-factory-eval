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
