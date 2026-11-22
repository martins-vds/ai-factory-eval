from collections.abc import Sequence
from typing import Protocol

from src.loans.domain import Loan


class LoanReader(Protocol):
    def list(self) -> Sequence[Loan]: ...

    def get(self, loan_id: str) -> Loan | None: ...
