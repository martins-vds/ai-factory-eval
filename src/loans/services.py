import csv
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


class Loans(Protocol):
    def all(self): ...

    def count(self): ...

    def find(self, loan_id): ...

    def create(self, **fields): ...


class LoanInputError(ValueError):
    def __init__(self, errors):
        self.errors = errors


class LoanNotFound(LookupError):
    pass


class LoanAlreadyReturned(ValueError):
    pass


def lend_loan(repository, member, isbn, today):
    errors = {}
    if member is None or not member.strip():
        errors['member'] = 'Enter a member name.'
    if isbn is None or not isbn.strip():
        errors['isbn'] = 'Enter an ISBN.'
    if errors:
        raise LoanInputError(errors)
    return repository.create(
        id=f'L{repository.count() + 1}',
        member=member,
        isbn=isbn,
        lent_on=today,
    )


def return_loan(repository, loan_id, today):
    loan = repository.find(loan_id)
    if loan is None:
        raise LoanNotFound(loan_id)
    if loan.returned_on is not None:
        raise LoanAlreadyReturned(loan_id)

    returned_loan = repository.return_if_unreturned(loan_id, today)
    if returned_loan is not None:
        return returned_loan

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


def list_loans_text(repository: Loans):
    return ''.join(loan_line(loan) for loan in repository.all())


def get_loan_text(repository: Loans, loan_id):
    loan = repository.find(loan_id)
    return loan_line(loan) if loan else None
