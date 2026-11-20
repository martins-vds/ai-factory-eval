import csv
from datetime import date
from io import StringIO

from .domain import Loan, due_date
from .ports import LoanRepository


def calculate_due_date(lent_on: date) -> date:
    return due_date(lent_on)


def list_loans(repository: LoanRepository) -> list[Loan]:
    return sorted(repository.list_all(), key=lambda loan: loan.id)


def get_loan(repository: LoanRepository, loan_id: str) -> Loan | None:
    return repository.find_by_id(loan_id)


def store_loan(repository: LoanRepository, loan: Loan) -> Loan:
    return repository.store(loan)


def export_loans(loans: list[Loan]) -> str:
    output = StringIO(newline='')
    writer = csv.writer(output, delimiter=';', lineterminator='\n')
    for loan in sorted(loans, key=lambda item: item.id):
        writer.writerow(
            (
                loan.id,
                loan.member,
                loan.isbn,
                loan.lent_on.isoformat(),
                loan.due_on.isoformat(),
                loan.returned_on.isoformat() if loan.returned_on else '',
            )
        )
    return output.getvalue()
