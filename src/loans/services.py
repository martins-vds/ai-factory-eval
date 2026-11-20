import csv
from io import StringIO

from .repository import LoanRepository


class LoanInputError(ValueError):
    def __init__(self, errors):
        self.errors = errors


def lend_loan(repository, member, isbn, today):
    errors = {}
    if member is None or not member.strip():
        errors['member'] = 'Enter a member name.'
    if isbn is None or not isbn.strip():
        errors['isbn'] = 'Enter an ISBN.'
    if errors:
        raise LoanInputError(errors)


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


def list_loans_text():
    return ''.join(loan_line(loan) for loan in LoanRepository().all())


def get_loan_text(loan_id):
    loan = LoanRepository().find(loan_id)
    return loan_line(loan) if loan else None
