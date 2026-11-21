from typing import Protocol

from .domain import Loan


class LoanRepository(Protocol):
    def list_all(self) -> list[Loan]: ...

    def get(self, loan_id: str) -> Loan | None: ...
