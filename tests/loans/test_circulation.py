from datetime import timedelta

import pytest
from django.utils import timezone
from django.utils.dateparse import parse_date

from src.loans.models import Loan


@pytest.mark.django_db
def test_lending_creates_a_loan_with_a_fourteen_day_due_date(client):
    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    lent_on = timezone.localdate()
    due_on = lent_on + timedelta(days=14)

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;dee;123;{lent_on.isoformat()};{due_on.isoformat()};\n'
    )


@pytest.mark.django_db
def test_returning_a_loan_records_the_server_date(client):
    response = client.post('/loans/L1/return')

    returned_on = timezone.localdate()
    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L1;ana;9780134685991;2026-01-02;2026-01-16;{returned_on.isoformat()}\n'
    )


@pytest.mark.django_db
def test_repeated_api_return_is_rejected_without_changing_the_original_date(client):
    original_date = parse_date('2026-01-20')

    response = client.post('/loans/L2/return')

    assert response.status_code == 409
    assert response.content.decode() == 'already returned\n'
    assert Loan.objects.get(pk='L2').returned_on == original_date


@pytest.mark.django_db
def test_lending_api_rejects_missing_and_blank_required_fields(client):
    for data, field in (
        ({'isbn': '123'}, 'member'),
        ({'member': 'reader'}, 'isbn'),
        ({'member': '  ', 'isbn': '123'}, 'member'),
        ({'member': 'reader', 'isbn': '  '}, 'isbn'),
    ):
        response = client.post('/loans', data)

        assert response.status_code == 400
        assert field in response.content.decode()


@pytest.mark.django_db
def test_lend_form_shows_field_errors_for_blank_values(client):
    response = client.post('/ui/loans/', {'member': '  ', 'isbn': ''})

    assert response.status_code == 400
    assert b'Enter a member name; blank values are not accepted.' in response.content
    assert b'Enter an ISBN; blank values are not accepted.' in response.content
