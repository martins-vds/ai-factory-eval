import csv
from collections.abc import Iterable
from datetime import date
from io import StringIO
from typing import Protocol


class Loan(Protocol):
    id: str
    member: str
    isbn: str
    lent_on: date
    due_on: date
    returned_on: date | None


class LoanStore(Protocol):
    def all(self) -> Iterable[Loan]: ...

    def find(self, loan_id: str) -> Loan | None: ...

    def next_id(self) -> str: ...

    def create(self, **fields) -> Loan: ...

    def set_return_date_if_unreturned(self, loan_id: str, returned_on: date) -> bool: ...


class InvalidLoan(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors
        super().__init__('invalid loan')


class LoanNotFound(Exception):
    pass


class LoanAlreadyReturned(Exception):
    pass


def lend_loan(
    store: LoanStore,
    member: str | None,
    isbn: str | None,
    lent_on: date,
) -> Loan:
    errors = {
        field: 'This field is required.'
        for field, value in (('member', member), ('isbn', isbn))
        if value is None or not value.strip()
    }
    if errors:
        raise InvalidLoan(errors)
    return store.create(
        id=store.next_id(),
        member=member,
        isbn=isbn,
        lent_on=lent_on,
    )


def return_loan(store: LoanStore, loan_id: str, returned_on: date) -> Loan:
    loan = store.find(loan_id)
    if loan is None:
        raise LoanNotFound(loan_id)
    if loan.returned_on is not None:
        raise LoanAlreadyReturned(loan_id)
    if not store.set_return_date_if_unreturned(loan_id, returned_on):
        raise LoanAlreadyReturned(loan_id)
    loan = store.find(loan_id)
    if loan is None:
        raise LoanNotFound(loan_id)
    return loan


def loan_line(loan: Loan) -> str:
    output = StringIO(newline='')
    writer = csv.writer(output, delimiter=';', lineterminator='\n')
    writer.writerow(
        [
            loan.id,
            loan.member,
            loan.isbn,
            loan.lent_on.isoformat(),
            loan.due_on.isoformat(),
            loan.returned_on.isoformat() if loan.returned_on else '',
        ]
    )
    return output.getvalue()


def list_loans_text(store: LoanStore) -> str:
    return ''.join(loan_line(loan) for loan in store.all())


def get_loan_text(store: LoanStore, loan_id: str) -> str | None:
    loan = store.find(loan_id)
    return loan_line(loan) if loan else None
