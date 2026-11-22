import csv
from io import StringIO
from datetime import timedelta

from src.loans.domain import Loan
from src.loans.ports import LoanReader


def loan_due_date(loan: Loan):
    return loan.lent_on + timedelta(days=14)


def list_loans(reader: LoanReader) -> list[Loan]:
    return sorted(reader.list(), key=lambda loan: loan.id)


def format_loan(loan: Loan) -> str:
    output = StringIO()
    writer = csv.writer(output, delimiter=';', lineterminator='\n')
    writer.writerow(
        [
            loan.id,
            loan.member,
            loan.isbn,
            loan.lent_on.isoformat(),
            loan_due_date(loan).isoformat(),
            loan.returned_on.isoformat() if loan.returned_on else '',
        ]
    )
    return output.getvalue()
