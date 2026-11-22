import csv
from io import StringIO

from src.loans.domain import Loan
from src.loans.ports import LoanRepository


class LoanNotFound(Exception):
    pass


class LoanCatalog:
    def __init__(self, repository: LoanRepository):
        self._repository = repository

    def list_loans(self) -> list[Loan]:
        return list(self._repository.list_loans())

    def get_loan(self, loan_id: str) -> Loan:
        loan = self._repository.get_loan(loan_id)
        if loan is None:
            raise LoanNotFound(loan_id)
        return loan

    def export_text(self) -> str:
        output = StringIO(newline='')
        writer = csv.writer(output, delimiter=';', lineterminator='\n')
        for loan in self.list_loans():
            writer.writerow(
                [
                    loan.loan_id,
                    loan.member,
                    loan.isbn,
                    loan.lent_on.isoformat(),
                    loan.due_on.isoformat(),
                    loan.returned_on.isoformat() if loan.returned_on else '',
                ]
            )
        return output.getvalue()

    def loan_text(self, loan: Loan) -> str:
        output = StringIO(newline='')
        writer = csv.writer(output, delimiter=';', lineterminator='\n')
        writer.writerow(
            [
                loan.loan_id,
                loan.member,
                loan.isbn,
                loan.lent_on.isoformat(),
                loan.due_on.isoformat(),
                loan.returned_on.isoformat() if loan.returned_on else '',
            ]
        )
        return output.getvalue()
