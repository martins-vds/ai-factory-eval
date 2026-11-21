from typing import Protocol

from src.loans.domain import Loan


class LoanRepository(Protocol):
    def list_all(self) -> list[Loan]: ...

    def get(self, loan_id: str) -> Loan | None: ...

    def save(self, loan: Loan) -> Loan: ...
