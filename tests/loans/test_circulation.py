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


@pytest.mark.django_db
def test_return_endpoint_records_today_and_returns_the_updated_loan(client):
    today = timezone.localdate()

    response = client.post('/loans/L1/return')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L1;ana;9780134685991;2026-01-02;2026-01-16;{today}\n'
    )
    assert client.get('/loans/L1').content.decode() == (
        f'L1;ana;9780134685991;2026-01-02;2026-01-16;{today}\n'
    )


@pytest.mark.django_db
def test_repeat_return_is_rejected_without_changing_the_original_date(client):
    response = client.post('/loans/L2/return')

    assert response.status_code == 409
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'loan already returned\n'
    assert client.get('/loans/L2').content.decode() == (
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
    )
