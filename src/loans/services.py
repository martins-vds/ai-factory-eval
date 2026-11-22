import csv
import io
from datetime import date

from src.loans.domain import Loan, due_date as loan_due_date
from src.loans.ports import LoanRepository


class LoanCatalog:
    def __init__(self, repository: LoanRepository):
        self._repository = repository

    def list_loans(self) -> list[Loan]:
        return sorted(self._repository.list_all(), key=lambda loan: loan.id)

    def get_loan(self, loan_id: str) -> Loan | None:
        return self._repository.find_by_id(loan_id)

    @staticmethod
    def due_date(lent_on: date) -> date:
        return loan_due_date(lent_on)

    @staticmethod
    def format_loan(loan: Loan) -> str:
        output = io.StringIO(newline='')
        csv.writer(output, delimiter=';', lineterminator='\n').writerow(
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
