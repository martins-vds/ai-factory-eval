from datetime import date

import pytest

from src.loans.services import LoanInputError, lend_loan


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
