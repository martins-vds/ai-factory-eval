from datetime import date, timedelta
from types import SimpleNamespace

import pytest

from src.loans.repository import LoanRepository
from src.loans.services import (
    InvalidLoan,
    LoanAlreadyReturned,
    LoanNotFound,
    lend_loan,
    loan_line,
    return_loan,
)


class LoanStore:
    def __init__(self):
        self.loans = {}

    def next_id(self):
        return f'L{len(self.loans) + 1}'

    def create(self, id, member, isbn, lent_on):
        loan = SimpleNamespace(
            id=id,
            member=member,
            isbn=isbn,
            lent_on=lent_on,
            due_on=lent_on + timedelta(days=14),
            returned_on=None,
        )
        self.loans[id] = loan
        return loan

    def find(self, loan_id):
        return self.loans.get(loan_id)

    def set_return_date_if_unreturned(self, loan_id, returned_on):
        loan = self.find(loan_id)
        if loan is None or loan.returned_on is not None:
            return False
        loan.returned_on = returned_on
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


def test_lending_preserves_field_values():
    loan = lend_loan(LoanStore(), ' reader ', ' 123 ', date(2026, 11, 1))

    assert loan.member == ' reader '
    assert loan.isbn == ' 123 '


@pytest.mark.django_db
def test_lending_use_case_sets_a_fourteen_day_due_date():
    loan = lend_loan(LoanRepository(), 'reader', '123', date(2026, 11, 1))

    assert loan.id == 'L4'
    assert loan.due_on == date(2026, 11, 15)


def test_lending_export_escapes_field_and_record_delimiters():
    loan = lend_loan(
        LoanStore(),
        'reader; one\nreader two',
        '123;456',
        date(2026, 11, 1),
    )

    assert loan_line(loan) == ('L1;"reader; one\nreader two";"123;456";2026-11-01;2026-11-15;\n')


def test_return_records_a_date_for_an_unreturned_loan():
    store = LoanStore()
    lend_loan(store, 'reader', '123', date(2026, 11, 1))

    loan = return_loan(store, 'L1', date(2026, 11, 21))

    assert loan.returned_on == date(2026, 11, 21)


def test_return_rejects_a_repeat_and_keeps_the_original_date():
    store = LoanStore()
    lend_loan(store, 'reader', '123', date(2026, 11, 1))
    return_loan(store, 'L1', date(2026, 11, 10))

    with pytest.raises(LoanAlreadyReturned):
        return_loan(store, 'L1', date(2026, 11, 21))

    assert store.find('L1').returned_on == date(2026, 11, 10)


def test_return_rejects_an_unknown_loan():
    with pytest.raises(LoanNotFound):
        return_loan(LoanStore(), 'missing', date(2026, 11, 21))
