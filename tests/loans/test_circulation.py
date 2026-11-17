from datetime import timedelta

import pytest
from django.utils import timezone


@pytest.mark.django_db
def test_lending_endpoint_creates_a_loan_with_fourteen_day_due_date(client):
    today = timezone.localdate()
    due_on = today + timedelta(days=14)

    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == f'L4;dee;123;{today};{due_on};\n'
    assert client.get('/loans/L4').content.decode() == (
        f'L4;dee;123;{today};{due_on};\n'
    )
