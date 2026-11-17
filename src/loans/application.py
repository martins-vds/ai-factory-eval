import csv
from io import StringIO

from .repository import find_by_id, list_all


def list_loans():
    return list_all()


def get_loan(loan_id):
    return find_by_id(loan_id)


def format_loan(loan):
    returned_on = loan.returned_on.isoformat() if loan.returned_on else ''
    row = StringIO(newline='')
    csv.writer(row, delimiter=';', lineterminator='').writerow(
        (
            loan.id,
            loan.member,
            loan.isbn,
            loan.lent_on.isoformat(),
            loan.due_on.isoformat(),
            returned_on,
        )
    )
    return row.getvalue()


def export_loans(loans):
    return '\n'.join(format_loan(loan) for loan in loans) + '\n'
