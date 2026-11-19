import csv
from io import StringIO

from .ports import LoanRepositoryPort, LoanRecord


class LoanInputError(ValueError):
    def __init__(self, fields):
        self.fields = fields
        super().__init__('member and isbn are required')


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


def get_loan(repository: LoanRepositoryPort, loan_id: str):
    return repository.find(loan_id)


def get_loan_text(repository: LoanRepositoryPort, loan_id: str):
    loan = get_loan(repository, loan_id)
    return loan_line(loan) if loan else None


def lend_loan(repository: LoanRepositoryPort, member: str | None, isbn: str | None, today):
    fields = {}
    if not member or not member.strip():
        fields['member'] = 'Member is required.'
    if not isbn or not isbn.strip():
        fields['isbn'] = 'ISBN is required.'
    if fields:
        raise LoanInputError(fields)
    return repository.create(member, isbn, today)


def return_loan(repository: LoanRepositoryPort, loan_id: str, returned_on):
    loan = repository.find(loan_id)
    if loan is None:
        return None
    if loan.returned_on is not None:
        raise LoanAlreadyReturned(loan_id)
    returned_loan = repository.mark_returned(loan_id, returned_on)
    if returned_loan is None:
        raise LoanAlreadyReturned(loan_id)
    return returned_loan
