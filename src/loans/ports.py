from collections.abc import Sequence
from typing import Protocol

from .domain import Loan


class LoanRepository(Protocol):
    def list_all(self) -> Sequence[Loan]: ...

    def find_by_id(self, loan_id: str) -> Loan | None: ...

    def save(self, loan: Loan) -> Loan: ...
