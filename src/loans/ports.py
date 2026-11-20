from typing import Protocol

from .domain import Loan


class LoanRepository(Protocol):
    def list_all(self) -> list[Loan]: ...

    def find_by_id(self, loan_id: str) -> Loan | None: ...

    def store(self, loan: Loan) -> Loan: ...
