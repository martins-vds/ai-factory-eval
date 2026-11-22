from datetime import timedelta

import pytest
from django.utils import timezone


@pytest.mark.django_db
def test_api_lends_a_book_and_returns_the_formatted_loan(client):
    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    today = timezone.localdate()
    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;dee;123;{today.isoformat()};{(today + timedelta(days=14)).isoformat()};\n'
    )
