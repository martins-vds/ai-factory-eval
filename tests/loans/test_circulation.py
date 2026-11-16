from datetime import timedelta

import pytest
from django.utils import timezone

from src.loans.models import Loan


@pytest.mark.django_db
def test_lending_api_creates_a_loan_with_a_fourteen_day_term(client):
    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    today = timezone.localdate()
    due_on = today + timedelta(days=14)
    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == f'L4;dee;123;{today};{due_on};\n'

    loan = Loan.objects.get(pk='L4')
    assert loan.member == 'dee'
    assert loan.isbn == '123'
    assert loan.lent_on == today


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('data', 'invalid_field'),
    [
        ({'isbn': '123'}, 'member'),
        ({'member': 'reader'}, 'isbn'),
        ({'member': '', 'isbn': '123'}, 'member'),
        ({'member': 'reader', 'isbn': '   '}, 'isbn'),
    ],
)
def test_lending_api_rejects_missing_or_blank_fields(client, data, invalid_field):
    response = client.post('/loans', data)

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'member and isbn are required\n'
    assert not Loan.objects.filter(pk='L4').exists()
