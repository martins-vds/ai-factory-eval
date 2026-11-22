from datetime import date

import pytest
from django.db import connection

from src.loans.domain import Loan
from src.loans.repository import DjangoLoanRepository


@pytest.mark.django_db
def test_repository_persists_loans_in_postgresql():
    assert connection.vendor == 'postgresql'
    loan = Loan('L4', 'dee', '123', date(2026, 11, 8), None)

    DjangoLoanRepository().save(loan)

    assert DjangoLoanRepository().get('L4') == loan
