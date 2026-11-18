import csv
from io import StringIO
from typing import Protocol


class LoanRepository(Protocol):
    def all(self): ...

    def find(self, loan_id): ...

    def create(self, **fields): ...

    def mark_returned(self, loan_id, returned_on): ...


class Clock(Protocol):
    def today(self): ...


class LoanInputError(ValueError):
    def __init__(self, field_errors):
        self.field_errors = field_errors
        super().__init__('member and isbn are required')


class LoanNotFound(LookupError):
    pass


class LoanAlreadyReturned(ValueError):
    pass


def lend_loan(member, isbn, repository, clock):
    field_errors = {
        field: f'{label} is required.'
        for field, value, label in (
            ('member', member, 'Member'),
            ('isbn', isbn, 'ISBN'),
        )
        if not isinstance(value, str) or not value.strip()
    }
    if field_errors:
        raise LoanInputError(field_errors)
    return repository.create(member=member, isbn=isbn, lent_on=clock.today())


def return_loan(loan_id, repository, clock):
    loan = repository.find(loan_id)
    if loan is None:
        raise LoanNotFound(loan_id)
    if loan.returned_on is not None:
        raise LoanAlreadyReturned(loan_id)
    return repository.mark_returned(loan_id, clock.today())


def list_loans(repository):
    return repository.all()


def get_loan(loan_id, repository):
    loan = repository.find(loan_id)
    if loan is None:
        raise LoanNotFound(loan_id)
    return loan


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


def list_loans_text(repository):
    return ''.join(loan_line(loan) for loan in repository.all())


def get_loan_text(loan_id, repository):
    try:
        loan = get_loan(loan_id, repository)
    except LoanNotFound:
        return None
    return loan_line(loan)
