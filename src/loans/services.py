import csv
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


class LoanRepositoryPort(Protocol):
    def all(self): ...

    def find(self, loan_id: str) -> LoanRecord | None: ...

    def next_id(self) -> str: ...

    def create(self, **fields) -> LoanRecord: ...

    def mark_returned(self, loan_id: str, returned_on: date) -> bool: ...


class LoanValidationError(ValueError):
    def __init__(self, errors):
        self.errors = errors
        super().__init__('member and isbn are required')


class LoanNotFound(LookupError):
    pass


class LoanAlreadyReturned(ValueError):
    pass


def loan_line(loan: LoanRecord):
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


def list_loans_text(repository: LoanRepositoryPort):
    return ''.join(loan_line(loan) for loan in repository.all())


def get_loan_text(repository: LoanRepositoryPort, loan_id: str):
    loan = repository.find(loan_id)
    return loan_line(loan) if loan else None


def lend_book(
    repository: LoanRepositoryPort,
    today: date,
    member: str | None,
    isbn: str | None,
) -> LoanRecord:
    errors = {}
    if not member or not member.strip():
        errors['member'] = 'This field is required.'
    if not isbn or not isbn.strip():
        errors['isbn'] = 'This field is required.'
    if errors:
        raise LoanValidationError(errors)

    return repository.create(
        id=repository.next_id(),
        member=member,
        isbn=isbn,
        lent_on=today,
    )


def return_book(repository: LoanRepositoryPort, loan_id: str, today: date) -> LoanRecord:
    loan = repository.find(loan_id)
    if loan is None:
        raise LoanNotFound(loan_id)
    if loan.returned_on is not None:
        raise LoanAlreadyReturned(loan_id)
    if not repository.mark_returned(loan_id, today):
        raise LoanAlreadyReturned(loan_id)
    loan.returned_on = today
    return loan
