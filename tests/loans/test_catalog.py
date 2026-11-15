import csv
import datetime
from io import StringIO

import pytest
from django.core.management import call_command
from django.db import connection

from src.loans.models import Loan


@pytest.mark.django_db
def test_list_returns_the_characterized_seed_export(client):
    response = client.get('/loans')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
        'L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03\n'
    )


@pytest.mark.django_db
def test_get_returns_one_characterized_loan(client):
    response = client.get('/loans/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'


@pytest.mark.django_db
def test_get_unknown_loan_returns_characterized_not_found_response(client):
    response = client.get('/loans/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_export_escapes_field_and_record_delimiters(client):
    Loan.objects.create(
        id='L4',
        member='reader;one\nsecond',
        isbn='123;456',
        lent_on=datetime.date(2026, 2, 1),
    )

    response = client.get('/loans/L4')
    fields = next(csv.reader(StringIO(response.content.decode(), newline=''), delimiter=';'))

    assert response.status_code == 200
    assert fields == [
        'L4',
        'reader;one\nsecond',
        '123;456',
        '2026-02-01',
        '2026-02-15',
        '',
    ]


@pytest.mark.django_db(transaction=True)
def test_migration_and_new_connection_preserve_persisted_loans(client):
    loan = Loan.objects.get(pk='L1')
    loan.member = 'updated reader'
    loan.save(update_fields=['member'])
    connection.close()

    call_command('migrate', verbosity=0)
    response = client.get('/loans/L1')

    assert response.status_code == 200
    assert response.content.decode() == 'L1;updated reader;9780134685991;2026-01-02;2026-01-16;\n'
