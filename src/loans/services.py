import csv
from io import StringIO

from .repository import LoanRepository


def lend_loan(member, isbn, lent_on):
    return LoanRepository().lend(member, isbn, lent_on)


def mark_loan_returned(loan_id, returned_on):
    return LoanRepository().mark_returned(loan_id, returned_on)


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
