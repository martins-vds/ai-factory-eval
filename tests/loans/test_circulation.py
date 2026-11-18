from datetime import date

import pytest

from src.loans.services import LoanValidationError, lend_loan


class LoanStore:
    def __init__(self):
        self.created = []

    def next_id(self):
        return f'L{len(self.created) + 1}'

    def create(self, **fields):
        self.created.append(fields)
        return fields


@pytest.mark.parametrize(
    ('member', 'isbn', 'field'),
    [
        (' \t', '123', 'member'),
        ('reader', '\n ', 'isbn'),
    ],
)
def test_lend_use_case_rejects_blank_fields_without_creating_a_loan(member, isbn, field):
    store = LoanStore()

    with pytest.raises(LoanValidationError) as error:
        lend_loan(member, isbn, date(2026, 11, 18), store)

    assert error.value.errors == {field: 'This field is required.'}
    assert store.created == []
