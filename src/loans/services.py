import csv
from io import StringIO

from .ports import Clock, LoanRepositoryPort


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


class LoanInputError(ValueError):
    def __init__(self, field_errors):
        self.field_errors = field_errors
        super().__init__('loan fields are invalid')


class LoanNotFound(LookupError):
    pass


class LoanAlreadyReturned(ValueError):
    pass


def list_loans_text(repository: LoanRepositoryPort):
    return ''.join(loan_line(loan) for loan in repository.all())


def get_loan_text(loan_id: str, repository: LoanRepositoryPort):
    loan = repository.find(loan_id)
    return loan_line(loan) if loan else None


def lend_book(
    member: str | None,
    isbn: str | None,
    repository: LoanRepositoryPort,
    clock: Clock,
):
    field_errors = {
        field: 'This field is required.'
        for field, value in (('member', member), ('isbn', isbn))
        if not isinstance(value, str) or not value.strip()
    }
    if field_errors:
        raise LoanInputError(field_errors)

    return repository.lend(member=member, isbn=isbn, lent_on=clock.today())


def return_book(loan_id: str, repository: LoanRepositoryPort, clock: Clock):
    loan = repository.find(loan_id)
    if loan is None:
        raise LoanNotFound(loan_id)
    if loan.returned_on is not None:
        raise LoanAlreadyReturned(loan_id)

    returned_on = clock.today()
    if not repository.mark_returned(loan_id, returned_on):
        raise LoanAlreadyReturned(loan_id)

    loan.returned_on = returned_on
    return loan
