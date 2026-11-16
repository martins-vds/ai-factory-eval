import csv
from io import StringIO

from src.loans.models import Loan


def format_loan(loan: Loan) -> str:
    output = StringIO(newline='')
    csv.writer(output, delimiter=';', lineterminator='').writerow(
        [
            loan.pk,
            loan.member,
            loan.isbn,
            loan.lent_on.isoformat(),
            loan.due_on.isoformat(),
            loan.returned_on.isoformat() if loan.returned_on else '',
        ]
    )
    return f'{output.getvalue()}\n'
