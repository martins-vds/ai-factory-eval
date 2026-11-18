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


@pytest.mark.django_db
def test_returning_a_loan_persists_today_and_returns_the_formatted_record(client):
    today = date.today()

    response = client.post('/loans/L1/return')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L1;ana;9780134685991;2026-01-02;2026-01-16;{today.isoformat()}\n'
    )
    saved_loan = client.get('/loans/L1')
    assert saved_loan.content == response.content
