from datetime import date

import pytest

from src.loans.repository import LoanRepository
from src.loans.services import LoanInputError, lend_loan


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('member', 'isbn', 'invalid_field'),
    [
        (None, '123', 'member'),
        (' \t', '123', 'member'),
        ('reader', None, 'isbn'),
        ('reader', ' \t', 'isbn'),
    ],
)
def test_lending_rejects_missing_or_blank_fields(member, isbn, invalid_field):
    loan_count = LoanRepository().all().count()

    with pytest.raises(LoanInputError) as error:
        lend_loan(
            repository=LoanRepository(),
            member=member,
            isbn=isbn,
            lent_on=date(2026, 11, 19),
        )

    assert error.value.fields == {invalid_field: 'This field is required.'}
    assert LoanRepository().all().count() == loan_count
