import csv
from datetime import date
from importlib import import_module
from io import StringIO

import pytest
from django.apps import apps
from django.db import connection, transaction

from src.loans import repository
from src.loans.models import Loan


@pytest.mark.django_db
def test_seed_migration_leaves_existing_catalog_data_untouched():
    Loan.objects.filter(pk='L1').update(member='stored member')
    migration = import_module('src.loans.migrations.0001_initial')

    with connection.schema_editor() as schema_editor:
        migration.seed_loans(apps, schema_editor)

    assert Loan.objects.get(pk='L1').member == 'stored member'


@pytest.mark.django_db
def test_seeded_loans_are_listed_in_id_order(client):
    response = client.get('/loans')

    assert response.status_code == 200
    assert response['Content-Type'].startswith('text/plain')
    assert response.content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
        'L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03\n'
    )


@pytest.mark.django_db
def test_loan_lookup_returns_one_line_or_characterized_not_found(client):
    response = client.get('/loans/L1')

    assert response.status_code == 200
    assert response['Content-Type'].startswith('text/plain')
    assert response.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'

    missing = client.get('/loans/unknown')
    assert missing.status_code == 404
    assert missing['Content-Type'].startswith('text/plain')
    assert missing.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_due_date_is_fourteen_calendar_days_after_lending():
    loan = Loan(
        id='L9',
        member='dee',
        isbn='123',
        lent_on=date(2026, 12, 25),
    )

    assert loan.due_on == date(2027, 1, 8)


@pytest.mark.django_db
def test_unreturned_loan_passes_model_validation():
    loan = Loan(id='L9', member='dee', isbn='123', lent_on=date(2026, 1, 1))
    return_field = Loan._meta.get_field('returned_on')

    assert return_field.null
    assert return_field.blank
    loan.full_clean()


@pytest.mark.django_db
def test_export_quotes_delimiters_and_record_breaks(client):
    Loan.objects.create(
        id='L9',
        member='Member; One',
        isbn='123\n456',
        lent_on='2026-01-01',
        returned_on=None,
    )

    response = client.get('/loans')

    rows = list(csv.reader(StringIO(response.content.decode()), delimiter=';'))
    assert rows[-1] == ['L9', 'Member; One', '123\n456', '2026-01-01', '2026-01-15', '']


@pytest.mark.django_db
def test_repository_writes_roll_back_with_the_transaction():
    loan = Loan(
        id='L9',
        member='dee',
        isbn='123',
        lent_on=date(2026, 1, 1),
    )

    with pytest.raises(RuntimeError), transaction.atomic():
        repository.save(loan)
        raise RuntimeError('abort write')

    assert not Loan.objects.filter(pk='L9').exists()


@pytest.mark.django_db
def test_saved_catalog_record_is_available_to_later_requests(client):
    repository.save(Loan(id='L9', member='dee', isbn='123', lent_on=date(2026, 1, 1)))

    response = client.get('/loans/L9')

    assert response.status_code == 200
    assert response.content.decode() == 'L9;dee;123;2026-01-01;2026-01-15;\n'


@pytest.mark.django_db
def test_catalog_pages_render_in_separate_ui_routes(client):
    response = client.get('/ui/loans/')

    assert response.status_code == 200
    assert b'Lending Library' in response.content
    assert b'9780134685991' in response.content
    assert b'/loans/L1' in response.content

    detail = client.get('/ui/loans/L1/')
    assert detail.status_code == 200
    assert b'2026-01-16' in detail.content
