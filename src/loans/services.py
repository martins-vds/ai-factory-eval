import csv
from io import StringIO

from .domain import Loan
from .ports import LoanRepository


def list_loans(repository: LoanRepository) -> list[Loan]:
    return sorted(repository.list_all(), key=lambda loan: loan.id)


def get_loan(repository: LoanRepository, loan_id: str) -> Loan | None:
    return repository.find_by_id(loan_id)


def store_loan(repository: LoanRepository, loan: Loan) -> Loan:
    return repository.store(loan)


def format_loan(loan: Loan) -> str:
    output = StringIO(newline='')
    writer = csv.writer(output, delimiter=';', lineterminator='\n')
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


def export_loans(repository: LoanRepository) -> str:
    return ''.join(format_loan(loan) for loan in list_loans(repository))
