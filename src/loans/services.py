import csv
from io import StringIO

from src.loans.domain import Loan
from src.loans.ports import LoanRepository


def list_loans(repository: LoanRepository) -> list[Loan]:
    return sorted(repository.all(), key=lambda loan: loan.id)


def get_loan(repository: LoanRepository, loan_id: str) -> Loan | None:
    return repository.find(loan_id)


def export_loans(repository: LoanRepository) -> str:
    output = StringIO(newline='')
    writer = csv.writer(output, delimiter=';', lineterminator='\n')
    loans = list_loans(repository)
    for loan in loans:
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
    return output.getvalue() or '\n'
