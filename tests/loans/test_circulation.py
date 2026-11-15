from datetime import date, timedelta

import pytest
from django.utils import timezone


@pytest.mark.django_db
def test_lending_creates_due_dated_loan_and_returns_formatted_record(client):
    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    fields = response.content.decode().strip().split(';')
    assert fields[:3] == ['L4', 'dee', '123']
    lent_on = date.fromisoformat(fields[3])
    assert lent_on == timezone.localdate()
    assert date.fromisoformat(fields[4]) == lent_on + timedelta(days=14)
    assert fields[5] == ''
    assert client.get('/loans/L4').content.decode() == response.content.decode()
