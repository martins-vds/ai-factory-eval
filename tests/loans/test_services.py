from datetime import date

import pytest

from src.loans.services import InvalidLoan, lend_loan


class LoanStore:
    def __init__(self):
        self.loans = {}

    def next_id(self):
        return f'L{len(self.loans) + 1}'

    def create(self, loan_id, member, isbn, lent_on):
        loan = {
            'id': loan_id,
            'member': member,
            'isbn': isbn,
            'lent_on': lent_on,
            'returned_on': None,
        }
        self.loans[loan_id] = loan
        return loan

    def find(self, loan_id):
        return self.loans.get(loan_id)

    def set_return_date_if_unreturned(self, loan_id, returned_on):
        loan = self.find(loan_id)
        if loan is None or loan['returned_on'] is not None:
            return False
        loan['returned_on'] = returned_on
        return True


@pytest.mark.parametrize(
    ('member', 'isbn', 'field'),
    [
        (None, '123', 'member'),
        ('', '123', 'member'),
        (' \t ', '123', 'member'),
        ('reader', None, 'isbn'),
        ('reader', '', 'isbn'),
        ('reader', '\n ', 'isbn'),
    ],
)
def test_lending_rejects_missing_or_blank_fields(member, isbn, field):
    store = LoanStore()

    with pytest.raises(InvalidLoan) as error:
        lend_loan(store, member, isbn, date(2026, 11, 21))

    assert error.value.field_errors == {field: 'This field is required.'}
    assert store.loans == {}
