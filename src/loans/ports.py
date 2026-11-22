from typing import Protocol, Sequence

from src.loans.domain import Loan


class LoanRepository(Protocol):
    def list_loans(self) -> Sequence[Loan]: ...

    def get_loan(self, loan_id: str) -> Loan | None: ...

    def add_loan(self, loan: Loan) -> Loan: ...
