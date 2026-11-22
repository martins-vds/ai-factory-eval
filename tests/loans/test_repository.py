from datetime import date

import pytest
from django.core.management import call_command
from django.db import connection

from src.loans.domain import Loan
from src.loans.repository import DjangoLoanRepository


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
