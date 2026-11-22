from datetime import date

import pytest
from django.core.management import call_command
from django.db import IntegrityError, connection

from src.loans.domain import Loan
from src.loans.models import LoanRecord
from src.loans.repository import DjangoLoanRepository
from src.loans.services import LoanCatalog


@pytest.mark.django_db
def test_repository_write_is_atomic_and_keeps_existing_record():
    repository = DjangoLoanRepository()
    loan = Loan('L4', 'dee', '123', date(2026, 1, 2))

    repository.create(loan)

    assert repository.find('L4') == loan
    with pytest.raises(IntegrityError):
        repository.create(Loan('L4', 'other', '456', date(2026, 1, 3)))
    assert repository.find('L4') == loan


def test_loan_model_keeps_characterized_storage_fields():
    assert LoanRecord._meta.ordering == ('id',)
    assert LoanRecord._meta.get_field('id').max_length == 255
    assert LoanRecord._meta.get_field('member').max_length == 255
    assert LoanRecord._meta.get_field('isbn').max_length == 255
    returned_on = LoanRecord._meta.get_field('returned_on')
    assert returned_on.null is True
    assert returned_on.blank is True


@pytest.mark.django_db(transaction=True)
def test_persisted_catalog_is_not_reseeded_after_database_reconnect():
    LoanRecord.objects.filter(pk='L1').update(member='persisted')
    connection.close()

    call_command('migrate', interactive=False, verbosity=0)
    loan = LoanCatalog(DjangoLoanRepository()).get('L1')

    assert loan is not None
    assert loan.member == 'persisted'
