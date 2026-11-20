from datetime import date

import pytest
from django.core.management import call_command
from django.db import IntegrityError

from src.loans.domain import Loan
from src.loans.models import LoanRecord
from src.loans.repositories import DjangoLoanRepository
from src.loans.services import store_loan


def test_return_date_is_nullable_and_blank_in_the_persistent_model():
    returned_on = LoanRecord._meta.get_field('returned_on')

    assert returned_on.null
    assert returned_on.blank


@pytest.mark.django_db
def test_failed_store_rolls_back_without_changing_existing_loan():
    repository = DjangoLoanRepository()
    existing = repository.find_by_id('L1')
    duplicate = Loan(
        id='L1',
        member='changed',
        isbn='123456',
        lent_on=date(2026, 2, 1),
        returned_on=None,
    )

    with pytest.raises(IntegrityError):
        store_loan(repository, duplicate)

    assert repository.find_by_id('L1') == existing


@pytest.mark.django_db
def test_stored_records_and_seed_values_survive_reapplying_migrations():
    repository = DjangoLoanRepository()
    extra_loan = Loan(
        id='L4',
        member='dee',
        isbn='123',
        lent_on=date(2026, 11, 20),
        returned_on=None,
    )
    store_loan(repository, extra_loan)

    call_command('migrate', interactive=False, verbosity=0)

    assert repository.find_by_id('L1').member == 'ana'
    assert repository.find_by_id('L4') == extra_loan
