import csv
from datetime import date
from io import StringIO

from .ports import LoanRecord, LoanRepositoryPort


class LoanInputError(Exception):
    def __init__(self, errors):
        self.errors = errors
        super().__init__('member and isbn are required')


class LoanNotFound(Exception):
    pass


class LoanAlreadyReturned(Exception):
    pass


def lending_errors(member: str | None, isbn: str | None) -> dict[str, str]:
    errors = {}
    if not member or not member.strip():
        errors['member'] = 'Member is required.'
    if not isbn or not isbn.strip():
        errors['isbn'] = 'ISBN is required.'
    return errors


def lend_loan(
    member: str | None,
    isbn: str | None,
    repository: LoanRepositoryPort,
    today: date,
) -> LoanRecord:
    errors = lending_errors(member, isbn)
    if errors:
        raise LoanInputError(errors)

    return repository.create(
        member=member,
        isbn=isbn,
        lent_on=today,
    )


def return_loan(
    loan_id: str,
    repository: LoanRepositoryPort,
    today: date,
) -> LoanRecord:
    loan = repository.find(loan_id)
    if loan is None:
        raise LoanNotFound(loan_id)
    if loan.returned_on is not None:
        raise LoanAlreadyReturned(loan_id)

    returned_loan = repository.record_return(loan_id, today)
    if returned_loan is not None:
        return returned_loan

    if repository.find(loan_id) is None:
        raise LoanNotFound(loan_id)
    raise LoanAlreadyReturned(loan_id)


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


def list_loans_text(repository: LoanRepositoryPort) -> str:
    return ''.join(loan_line(loan) for loan in repository.all())


def get_loan_text(loan_id: str, repository: LoanRepositoryPort) -> str | None:
    loan = repository.find(loan_id)
    return loan_line(loan) if loan else None
