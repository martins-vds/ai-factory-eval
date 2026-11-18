from datetime import date, timedelta

import pytest


@pytest.mark.django_db
def test_lending_creates_a_persisted_fourteen_day_loan(client):
    today = date.today()

    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;dee;123;{today.isoformat()};{(today + timedelta(days=14)).isoformat()};\n'
    )
    saved_loan = client.get('/loans/L4')
    assert saved_loan.status_code == 200
    assert saved_loan.content == response.content
