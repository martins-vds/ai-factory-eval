import csv
from datetime import date
from io import StringIO

import pytest
from django.core.management import call_command

from src.loans.models import Loan


@pytest.mark.django_db
def test_list_returns_the_seeded_loans_in_legacy_order(client):
    response = client.get('/loans')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
        'L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03\n'
    )


@pytest.mark.django_db
def test_lookup_returns_one_loan_or_the_legacy_not_found_response(client):
    response = client.get('/loans/L1')

    assert response.status_code == 200
    assert response.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'

    missing = client.get('/loans/unknown')
    assert missing.status_code == 404
    assert missing.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_export_escapes_field_and_record_delimiters(client):
    Loan.objects.create(
        id='L4',
        member='member;name',
        isbn='isbn\nedition',
        lent_on=date(2026, 2, 1),
    )

    response = client.get('/loans')
    rows = list(csv.reader(StringIO(response.content.decode()), delimiter=';'))

    assert rows[-1] == [
        'L4',
        'member;name',
        'isbn\nedition',
        '2026-02-01',
        '2026-02-15',
        '',
    ]


@pytest.mark.django_db
def test_existing_loan_survives_a_repeated_migration(client):
    Loan.objects.filter(pk='L1').update(member='persistent member')

    call_command('migrate', interactive=False, verbosity=0)

    response = client.get('/loans/L1')
    assert response.content.decode() == (
        'L1;persistent member;9780134685991;2026-01-02;2026-01-16;\n'
    )
