from typing import Protocol, Sequence

from src.loans.domain import Loan


class LoanReader(Protocol):
    def list(self) -> Sequence[Loan]: ...
