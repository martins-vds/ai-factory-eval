from datetime import date

import pytest
from django.core.management import call_command
from django.db import IntegrityError, connection

from src.loans.domain import Loan
from src.loans.models import LoanRecord
from src.loans.repository import DjangoLoanRepository


@pytest.mark.django_db
def test_repository_write_is_atomic_and_keeps_existing_record():
    repository = DjangoLoanRepository()
    loan = Loan('L4', 'dee', '123', date(2026, 1, 2))

    repository.create(loan)

    assert repository.find('L4') == loan
    with pytest.raises(IntegrityError):
        repository.create(Loan('L4', 'other', '456', date(2026, 1, 3)))
    assert repository.find('L4') == loan


@pytest.mark.django_db(transaction=True)
def test_persisted_catalog_is_not_reseeded_after_database_reconnect(client):
    LoanRecord.objects.filter(pk='L1').update(member='persisted')
    connection.close()

    call_command('migrate', interactive=False, verbosity=0)
    response = client.get('/loans/L1')

    assert response.status_code == 200
    assert response.content.decode() == ('L1;persisted;9780134685991;2026-01-02;2026-01-16;\n')
