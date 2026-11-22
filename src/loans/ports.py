from collections.abc import Sequence
from typing import Protocol

from src.loans.domain import Loan


class LoanRepository(Protocol):
    def all(self) -> Sequence[Loan]: ...

    def find(self, loan_id: str) -> Loan | None: ...

    def create(self, loan: Loan) -> Loan: ...
