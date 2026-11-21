import csv
from io import StringIO

from .domain import Loan
from .ports import LoanRepository


class LoanNotFound(Exception):
    pass


class LoanCatalog:
    def __init__(self, repository: LoanRepository):
        self._repository = repository

    def list_loans(self) -> list[Loan]:
        return self._repository.list_all()

    def get_loan(self, loan_id: str) -> Loan:
        loan = self._repository.get(loan_id)
        if loan is None:
            raise LoanNotFound(loan_id)
        return loan

    def text_export(self) -> str:
        return ''.join(format_loan(loan) for loan in self.list_loans())


def format_loan(loan: Loan) -> str:
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
