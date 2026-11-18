import csv
from io import StringIO
from typing import Protocol


class LoanRecord(Protocol):
    id: str
    member: str
    isbn: str
    lent_on: object
    due_on: object
    returned_on: object | None


class LoanRepositoryPort(Protocol):
    def all(self): ...

    def find(self, loan_id: str) -> LoanRecord | None: ...

    def next_id(self) -> str: ...

    def create(self, **fields) -> LoanRecord: ...

    def mark_returned(self, loan_id: str, returned_on) -> LoanRecord | None: ...


class Clock(Protocol):
    def today(self): ...


class LoanInputError(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors
        super().__init__('member and isbn are required')


class LoanNotFound(Exception):
    pass


class LoanAlreadyReturned(Exception):
    pass


def lend_loan(repository: LoanRepositoryPort, clock: Clock, member: str | None, isbn: str | None):
    field_errors = {}
    if member is None or not member.strip():
        field_errors['member'] = 'This field is required.'
    if isbn is None or not isbn.strip():
        field_errors['isbn'] = 'This field is required.'
    if field_errors:
        raise LoanInputError(field_errors)

    return repository.create(
        id=repository.next_id(),
        member=member,
        isbn=isbn,
        lent_on=clock.today(),
    )


def return_loan(repository: LoanRepositoryPort, clock: Clock, loan_id: str):
    loan = repository.find(loan_id)
    if loan is None:
        raise LoanNotFound(loan_id)
    if loan.returned_on is not None:
        raise LoanAlreadyReturned(loan_id)

    returned = repository.mark_returned(loan_id, clock.today())
    if returned is not None:
        return returned
    if repository.find(loan_id) is None:
        raise LoanNotFound(loan_id)
    raise LoanAlreadyReturned(loan_id)


def loan_line(loan):
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


def get_loan_text(repository: LoanRepositoryPort, loan_id):
    loan = repository.find(loan_id)
    return loan_line(loan) if loan else None
