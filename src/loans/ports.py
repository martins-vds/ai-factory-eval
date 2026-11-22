from typing import Protocol, Sequence

from src.loans.domain import Loan


class LoanRepository(Protocol):
    def list_all(self) -> Sequence[Loan]: ...

    def find_by_id(self, loan_id: str) -> Loan | None: ...

    def save(self, loan: Loan) -> None: ...
