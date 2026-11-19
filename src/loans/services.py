import csv
from io import StringIO
from typing import Protocol


class LoanRepositoryPort(Protocol):
    def atomic(self): ...

    def all(self): ...

    def create(self, **fields): ...

    def find(self, loan_id): ...

    def find_for_update(self, loan_id): ...

    def save(self, loan): ...


class LoanInputError(Exception):
    def __init__(self, fields):
        self.fields = fields
        super().__init__('Member and ISBN are required.')


class LoanNotFound(Exception):
    pass


class LoanAlreadyReturned(Exception):
    def __init__(self, loan):
        self.loan = loan
        super().__init__(loan.id)


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


def get_loan_text(loan_id, repository: LoanRepositoryPort):
    loan = repository.find(loan_id)
    return loan_line(loan) if loan else None


def lend_loan(
    *,
    repository: LoanRepositoryPort,
    member: str | None,
    isbn: str | None,
    lent_on,
):
    fields = {'member': member, 'isbn': isbn}
    errors = {
        name: 'This field is required.'
        for name, value in fields.items()
        if not isinstance(value, str) or not value.strip()
    }
    if errors:
        raise LoanInputError(errors)

    return repository.create(
        id=f'L{len(repository.all()) + 1}',
        member=member,
        isbn=isbn,
        lent_on=lent_on,
    )


def return_loan(*, repository: LoanRepositoryPort, loan_id: str, returned_on):
    with repository.atomic():
        loan = repository.find_for_update(loan_id)
        if loan is None:
            raise LoanNotFound(loan_id)
        if loan.returned_on is not None:
            raise LoanAlreadyReturned(loan)
        loan.returned_on = returned_on
        return repository.save(loan)
