from datetime import timedelta

import pytest
from django.utils import timezone

from src.loans.models import Loan


@pytest.mark.django_db
def test_lending_creates_a_durable_fourteen_day_loan(client):
    today = timezone.localdate()

    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;dee;123;{today.isoformat()};{(today + timedelta(days=14)).isoformat()};\n'
    )
    assert client.get('/loans/L4').content == response.content
    assert Loan.objects.get(pk='L4').lent_on == today
