from datetime import date

import pytest
from django.db import connection

from src.loans.models import Loan
from src.loans.repository import create_loan


@pytest.mark.django_db
def test_catalog_list_and_lookup_match_characterized_output(client):
    response = client.get('/loans')

    assert response.status_code == 200
    assert response['Content-Type'].startswith('text/plain')
    assert response.content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
        'L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03\n'
    )

    detail = client.get('/loans/L1')
    assert detail.status_code == 200
    assert detail.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'


@pytest.mark.django_db
def test_unknown_loan_returns_characterized_not_found_response(client):
    response = client.get('/loans/unknown')

    assert response.status_code == 404
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_due_date_and_export_escape_delimiters(client):
    loan = create_loan(
        loan_id='L4',
        member='Reader; One',
        isbn='9780000000000',
        lent_on=date(2024, 2, 20),
    )

    assert loan.due_on == date(2024, 3, 5)
    response = client.get('/loans/L4')

    assert response.status_code == 200
    assert response.content.decode() == (
        'L4;"Reader; One";9780000000000;2024-02-20;2024-03-05;\n'
    )


@pytest.mark.django_db(transaction=True)
def test_loan_survives_database_connection_restart(client):
    create_loan(
        loan_id='PERSISTED',
        member='Reader',
        isbn='9780000000000',
        lent_on=date(2026, 11, 1),
    )
    connection.close()

    response = client.get('/loans/PERSISTED')

    assert response.status_code == 200
    assert response.content.decode() == (
        'PERSISTED;Reader;9780000000000;2026-11-01;2026-11-15;\n'
    )
    assert Loan.objects.filter(pk='PERSISTED').exists()
