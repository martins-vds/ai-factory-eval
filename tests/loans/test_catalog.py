import pytest
from datetime import date

from src.loans.models import Loan


@pytest.mark.django_db
def test_loan_list_matches_characterized_export(client):
    response = client.get('/loans')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
        'L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03\n'
    )


@pytest.mark.django_db
def test_loan_list_orders_records_by_id(client):
    Loan.objects.create(
        id='L10',
        member='dee',
        isbn='123',
        lent_on=date(2026, 11, 8),
    )

    response = client.get('/loans')

    assert response.content.decode().splitlines()[3].startswith('L10;')


@pytest.mark.django_db
def test_loan_lookup_returns_record_or_characterized_not_found(client):
    response = client.get('/loans/L1')

    assert response.status_code == 200
    assert response.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'

    missing = client.get('/loans/unknown')

    assert missing.status_code == 404
    assert missing.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_due_date_is_fourteen_calendar_days_after_lending():
    loan = Loan.objects.get(pk='L1')

    assert loan.due_on == date(2026, 1, 16)


@pytest.mark.django_db
def test_export_quotes_delimiter_characters(client):
    Loan.objects.create(
        id='L4',
        member='a;b',
        isbn='123;456',
        lent_on=date(2026, 11, 8),
    )

    response = client.get('/loans/L4')

    assert response.content.decode() == 'L4;"a;b";"123;456";2026-11-08;2026-11-22;\n'


def test_admin_is_not_installed(client):
    assert client.get('/admin/login/').status_code == 404
