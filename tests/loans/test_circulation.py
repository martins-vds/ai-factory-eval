from datetime import timedelta

import pytest
from django.utils import timezone


@pytest.mark.django_db
def test_lend_endpoint_creates_a_loan_with_fourteen_day_due_date(client):
    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    today = timezone.localdate()
    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;dee;123;{today};{today + timedelta(days=14)};\n'
    )
