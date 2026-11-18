import csv
from io import StringIO
from typing import Protocol


class LoanRepository(Protocol):
    def all(self): ...

    def find(self, loan_id): ...

    def create(self, **fields): ...


class Clock(Protocol):
    def today(self): ...


class LoanInputError(ValueError):
    def __init__(self, field_errors):
        self.field_errors = field_errors
        super().__init__('member and isbn are required')


def lend_loan(member, isbn, repository, clock):
    field_errors = {
        field: 'This field is required.'
        for field, value in (('member', member), ('isbn', isbn))
        if not isinstance(value, str) or not value.strip()
    }
    if field_errors:
        raise LoanInputError(field_errors)
    return repository.create(member=member, isbn=isbn, lent_on=clock.today())


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
    loan = repository.find(loan_id)
    return loan_line(loan) if loan else None
