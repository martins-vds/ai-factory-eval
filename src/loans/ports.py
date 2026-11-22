from collections.abc import Sequence
from typing import Protocol

from .domain import Loan


class LoanRepository(Protocol):
    def all(self) -> Sequence[Loan]: ...

    def find(self, loan_id: str) -> Loan | None: ...
