from datetime import timedelta

import pytest
from django.utils import timezone

from src.loans.models import Loan


def server_today():
    return timezone.localdate(timezone.now(), timezone.get_default_timezone())


@pytest.mark.django_db
def test_lend_endpoint_creates_a_loan_with_a_fourteen_day_due_date(client):
    today = server_today()

    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;dee;123;{today.isoformat()};{(today + timedelta(days=14)).isoformat()};\n'
    )
    assert Loan.objects.get(pk='L4').lent_on == today


@pytest.mark.parametrize(
    ('member', 'isbn'),
    [
        ('', '123'),
        (' \t ', '123'),
        ('reader', ''),
        ('reader', '\n '),
        (None, '123'),
        ('reader', None),
    ],
)
@pytest.mark.django_db
def test_lend_endpoint_rejects_missing_or_blank_fields(client, member, isbn):
    data = {
        field: value for field, value in (('member', member), ('isbn', isbn)) if value is not None
    }
    response = client.post('/loans', data)

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'member and isbn are required\n'
    assert Loan.objects.count() == 3


@pytest.mark.django_db
def test_return_endpoint_records_the_date(client):
    today = server_today()

    response = client.post('/loans/L1/return')

    assert response.status_code == 200
    assert response.content.decode() == (
        f'L1;ana;9780134685991;2026-01-02;2026-01-16;{today.isoformat()}\n'
    )
    assert Loan.objects.get(pk='L1').returned_on == today


@pytest.mark.django_db
def test_return_endpoint_rejects_a_repeat_and_keeps_the_original_date(client):
    original_date = Loan.objects.get(pk='L2').returned_on

    response = client.post('/loans/L2/return')

    assert response.status_code == 409
    assert Loan.objects.get(pk='L2').returned_on == original_date


@pytest.mark.django_db
def test_return_endpoint_reports_an_unknown_loan(client):
    response = client.post('/loans/missing/return')

    assert response.status_code == 404
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_lend_endpoint_escapes_field_and_record_delimiters(client):
    today = server_today()

    response = client.post(
        '/loans',
        {'member': 'dee; reader\nsecond', 'isbn': '123;456'},
    )

    assert response.status_code == 201
    assert response.content.decode() == (
        f'L4;"dee; reader\nsecond";"123;456";{today.isoformat()};'
        f'{(today + timedelta(days=14)).isoformat()};\n'
    )
