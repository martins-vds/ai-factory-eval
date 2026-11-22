import csv
from io import StringIO
from datetime import date
from typing import Protocol


class LoanRepositoryPort(Protocol):
    def all(self): ...

    def find(self, loan_id): ...

    def next_id(self): ...

    def create(self, **fields): ...

    def mark_returned(self, loan_id, returned_on): ...


class InvalidLoanInput(ValueError):
    def __init__(self, errors):
        self.errors = errors
        super().__init__('Loan fields are required.')


class AlreadyReturned(ValueError):
    pass


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


def list_loans(repository: LoanRepositoryPort):
    return repository.all()


def list_loans_text(repository: LoanRepositoryPort):
    return ''.join(loan_line(loan) for loan in list_loans(repository))


def get_loan(loan_id, repository: LoanRepositoryPort):
    return repository.find(loan_id)


def get_loan_text(loan_id, repository: LoanRepositoryPort):
    loan = get_loan(loan_id, repository)
    return loan_line(loan) if loan else None


def lend_loan(member: str | None, isbn: str | None, repository: LoanRepositoryPort, today: date):
    errors = {}
    if member is None or not member.strip():
        errors['member'] = 'This field is required.'
    if isbn is None or not isbn.strip():
        errors['isbn'] = 'This field is required.'
    if errors:
        raise InvalidLoanInput(errors)

    return repository.create(
        id=repository.next_id(),
        member=member,
        isbn=isbn,
        lent_on=today,
    )


def return_loan(loan_id, repository: LoanRepositoryPort, today: date):
    loan = repository.find(loan_id)
    if loan is None:
        return None
    if loan.returned_on is not None:
        raise AlreadyReturned

    returned_loan = repository.mark_returned(loan_id, today)
    if returned_loan is None:
        raise AlreadyReturned
    return returned_loan
