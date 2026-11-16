from datetime import date, timedelta

import pytest


@pytest.mark.django_db
def test_lending_api_creates_and_formats_a_loan(client):
    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    today = date.today()
    due_on = today + timedelta(days=14)
    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == f'L4;dee;123;{today};{due_on};\n'
