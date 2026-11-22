from .domain import Loan, LoanNotFound, export_loan
from .ports import LoanRepository


class LoanCatalog:
    def __init__(self, repository: LoanRepository) -> None:
        self._repository = repository

    def list_loans(self) -> list[Loan]:
        return sorted(self._repository.list_all(), key=lambda loan: loan.id)

    def get_loan(self, loan_id: str) -> Loan:
        loan = self._repository.find_by_id(loan_id)
        if loan is None:
            raise LoanNotFound(loan_id)
        return loan

    def export_loans(self) -> str:
        return ''.join(export_loan(loan) for loan in self.list_loans())

    def export_loan(self, loan_id: str) -> str:
        return export_loan(self.get_loan(loan_id))
