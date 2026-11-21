import csv
from collections.abc import Iterable
from datetime import date
from io import StringIO
from typing import Protocol


class LoanRecord(Protocol):
    id: str
    member: str
    isbn: str
    lent_on: date
    due_on: date
    returned_on: date | None


class LoanStore(Protocol):
    def all(self) -> Iterable[LoanRecord]: ...

    def find(self, loan_id: str) -> LoanRecord | None: ...

    def create(self, **fields) -> LoanRecord: ...

    def mark_returned(self, loan_id: str, returned_on: date) -> LoanRecord | None: ...


class LoanInputError(ValueError):
    def __init__(self, errors):
        self.errors = errors


class LoanNotFound(LookupError):
    pass


class LoanAlreadyReturned(ValueError):
    pass


def loan_line(loan: LoanRecord) -> str:
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


def list_loans(store: LoanStore) -> Iterable[LoanRecord]:
    return store.all()


def get_loan(store: LoanStore, loan_id: str) -> LoanRecord | None:
    return store.find(loan_id)


def list_loans_text(store: LoanStore) -> str:
    return ''.join(loan_line(loan) for loan in list_loans(store))


def get_loan_text(store: LoanStore, loan_id: str) -> str | None:
    loan = get_loan(store, loan_id)
    return loan_line(loan) if loan else None


def lend_loan(
    store: LoanStore,
    member: str | None,
    isbn: str | None,
    lent_on: date | None = None,
) -> LoanRecord:
    errors = {
        field: 'This field is required.'
        for field, value in (('member', member), ('isbn', isbn))
        if not value or not value.strip()
    }
    if errors:
        raise LoanInputError(errors)

    return store.create(
        id=f'L{len(list_loans(store)) + 1}',
        member=member,
        isbn=isbn,
        lent_on=lent_on or date.today(),
    )


def return_loan(
    loan_id: str,
    store: LoanStore,
    returned_on: date | None = None,
) -> LoanRecord:
    loan = get_loan(store, loan_id)
    if loan is None:
        raise LoanNotFound(loan_id)
    if loan.returned_on is not None:
        raise LoanAlreadyReturned(loan_id)

    updated = store.mark_returned(loan_id, returned_on or date.today())
    if updated is None:
        raise LoanAlreadyReturned(loan_id)
    return updated
