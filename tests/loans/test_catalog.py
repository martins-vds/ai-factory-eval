from datetime import date
from importlib import import_module

import pytest
from django.apps import apps
from django.db import IntegrityError, connection
from django.urls import reverse

from src.loans.models import Loan
from src.loans.repository import save_loan


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

    assert response.content.decode().splitlines()[1].startswith('L10;')


@pytest.mark.django_db
def test_loan_lookup_returns_record_or_characterized_not_found(client):
    response = client.get('/loans/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'

    missing = client.get('/loans/unknown')

    assert missing.status_code == 404
    assert missing['Content-Type'] == 'text/plain'
    assert missing.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_due_date_is_fourteen_calendar_days_after_lending():
    loan = Loan.objects.get(pk='L1')

    assert loan.due_on == date(2026, 1, 16)


@pytest.mark.django_db
def test_export_quotes_delimiter_characters(client):
    Loan.objects.create(
        id='L4',
        member='a;"b',
        isbn='123\n456',
        lent_on=date(2026, 11, 8),
    )

    response = client.get('/loans/L4')

    assert response.content.decode() == 'L4;"a;""b";"123\n456";2026-11-08;2026-11-22;\n'


@pytest.mark.django_db
def test_catalog_detail_page_shows_loan_information(client):
    response = client.get('/ui/loans/L1/')

    assert response.status_code == 200
    assert b'9780134685991' in response.content


@pytest.mark.django_db
def test_catalog_list_page_renders_seeded_records(client):
    response = client.get('/ui/loans/')

    assert response.status_code == 200
    assert b'Books in good company.' in response.content
    assert b'ana' in response.content


def test_named_routes_match_the_public_paths():
    assert reverse('loan-list') == '/loans'
    assert reverse('loan-detail', kwargs={'loan_id': 'L1'}) == '/loans/L1'
    assert reverse('loan-catalog') == '/ui/loans/'
    assert reverse('loan-page', kwargs={'loan_id': 'L1'}) == '/ui/loans/L1/'


def test_unreturned_loan_fields_allow_null_and_blank():
    returned_on = Loan._meta.get_field('returned_on')

    assert returned_on.null
    assert returned_on.blank


@pytest.mark.django_db
def test_seed_migration_fills_missing_records_without_overwriting_existing_ones():
    Loan.objects.filter(pk='L1').update(member='existing record')
    Loan.objects.filter(pk='L2').delete()
    migration = import_module('src.loans.migrations.0002_seed_loans')

    migration.seed_loans(apps, None)

    assert Loan.objects.get(pk='L1').member == 'existing record'
    assert Loan.objects.filter(pk='L2').exists()


@pytest.mark.django_db(transaction=True, serialized_rollback=True)
def test_loan_record_survives_database_connection_reopen(client):
    save_loan(
        Loan(
            id='L4',
            member='dee',
            isbn='123',
            lent_on=date(2026, 11, 8),
        )
    )
    connection.close()

    response = client.get('/loans/L4')

    assert response.content.decode() == 'L4;dee;123;2026-11-08;2026-11-22;\n'


@pytest.mark.django_db
def test_repository_rolls_back_a_failed_write():
    with pytest.raises(IntegrityError):
        save_loan(
            Loan(
                id='L4',
                member='dee',
                isbn='123',
                lent_on=None,
            )
        )

    assert not Loan.objects.filter(pk='L4').exists()
    assert Loan.objects.get(pk='L1').member == 'ana'


def test_admin_is_not_installed(client):
    assert client.get('/admin/login/').status_code == 404
