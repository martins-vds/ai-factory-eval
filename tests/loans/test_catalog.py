import csv
import datetime
import io

import pytest
from django.core.management import call_command

from src.loans.models import Loan


@pytest.mark.django_db
def test_list_returns_seeded_loans_in_characterized_text_format(client):
    response = client.get('/loans')

    assert response.status_code == 200
    assert response['Content-Type'].startswith('text/plain')
    assert response.content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
        'L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03\n'
    )


@pytest.mark.django_db
def test_lookup_returns_formatted_loan_and_not_found_text(client):
    response = client.get('/loans/L1')

    assert response.status_code == 200
    assert response.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'

    missing = client.get('/loans/missing')

    assert missing.status_code == 404
    assert missing.content == b'no such loan\n'


@pytest.mark.django_db
def test_text_export_escapes_field_and_record_delimiters(client):
    Loan.objects.create(
        id='L4',
        member='reader; with\nan alias',
        isbn='123;"456"',
        lent_on=datetime.date(2026, 1, 1),
    )

    response = client.get('/loans')
    records = list(csv.reader(io.StringIO(response.content.decode()), delimiter=';'))

    assert records[-1] == [
        'L4',
        'reader; with\nan alias',
        '123;"456"',
        '2026-01-01',
        '2026-01-15',
        '',
    ]
    assert response.content.endswith(b'\n')


@pytest.mark.django_db
def test_reapplying_migrations_does_not_replace_persisted_loan_data():
    Loan.objects.filter(pk='L1').update(member='changed member')

    call_command('migrate', verbosity=0)

    assert Loan.objects.get(pk='L1').member == 'changed member'


@pytest.mark.django_db
def test_django_admin_route_is_not_installed(client):
    assert client.get('/admin/login/').status_code == 404
