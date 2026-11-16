import csv
from datetime import date
from io import StringIO

from .repository import LoanRepository


def lend_loan(member, isbn):
    repository = LoanRepository()
    return repository.create(
        id=f'L{repository.all().count() + 1}',
        member=member,
        isbn=isbn,
        lent_on=date.today(),
    )


def return_loan(loan_id):
    return LoanRepository().mark_returned(loan_id, date.today())


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
