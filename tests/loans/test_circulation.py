from datetime import date

import pytest

from src.loans.services import LoanInputError, lend_loan
from src.loans.repository import LoanRepository


@pytest.mark.parametrize(
    ('member', 'isbn', 'expected_errors'),
    [
        ('', '9780134685991', {'member': 'Enter a member name.'}),
        (' \t', '9780134685991', {'member': 'Enter a member name.'}),
        ('reader', '', {'isbn': 'Enter an ISBN.'}),
        ('reader', ' \t', {'isbn': 'Enter an ISBN.'}),
        (None, None, {'member': 'Enter a member name.', 'isbn': 'Enter an ISBN.'}),
    ],
)
def test_lending_rejects_empty_or_whitespace_required_fields(member, isbn, expected_errors):
    with pytest.raises(LoanInputError) as error:
        lend_loan(None, member, isbn, date(2026, 11, 20))

    assert error.value.errors == expected_errors


@pytest.mark.django_db
def test_lending_persists_values_exactly_and_sets_the_fourteen_day_term():
    loan = lend_loan(LoanRepository(), ' m1 ', ' 978-0 ', date(2026, 11, 20))

    assert loan.id == 'L4'
    assert loan.member == ' m1 '
    assert loan.isbn == ' 978-0 '
    assert loan.lent_on == date(2026, 11, 20)
    assert loan.due_on == date(2026, 12, 4)
