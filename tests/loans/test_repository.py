from datetime import date
from importlib import import_module
from types import SimpleNamespace

import pytest
from django.apps import apps
from django.core.management import call_command
from django.db import connection

from src.loans.domain import Loan
from src.loans.models import LoanRecord
from src.loans.repository import DjangoLoanRepository


def test_returned_date_field_allows_unreturned_loans():
    field = LoanRecord._meta.get_field('returned_on')

    assert field.null
    assert field.blank


@pytest.mark.django_db
def test_repository_writes_inside_an_atomic_transaction():
    writes = []

    def check_write_transaction(execute, sql, params, many, context):
        if sql.lstrip().upper().startswith(('INSERT', 'UPDATE')):
            writes.append(sql)
            assert connection.in_atomic_block
        return execute(sql, params, many, context)

    with connection.execute_wrapper(check_write_transaction):
        DjangoLoanRepository().save(Loan('L4', 'dee', '123', date(2026, 11, 8), None))

    assert writes


@pytest.mark.django_db
def test_repository_persists_loans_in_postgresql():
    assert connection.vendor == 'postgresql'
    loan = Loan('L4', 'dee', '123', date(2026, 11, 8), None)

    DjangoLoanRepository().save(loan)

    assert DjangoLoanRepository().get('L4') == loan


@pytest.mark.django_db(transaction=True)
def test_reapplying_migrations_does_not_replace_existing_seed_records():
    repository = DjangoLoanRepository()
    seed = repository.get('L1')
    updated = Loan(seed.id, 'changed member', seed.isbn, seed.lent_on, seed.returned_on)
    repository.save(updated)

    call_command('migrate', 'loans', verbosity=0)

    assert DjangoLoanRepository().get('L1').member == 'changed member'


@pytest.mark.django_db
def test_seed_migration_preserves_existing_record_values():
    repository = DjangoLoanRepository()
    seed = repository.get('L1')
    repository.save(Loan(seed.id, 'changed member', seed.isbn, seed.lent_on, seed.returned_on))
    migration = import_module('src.loans.migrations.0001_initial')

    migration.seed_loans(apps, SimpleNamespace(connection=connection))

    assert repository.get('L1').member == 'changed member'
