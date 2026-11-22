from datetime import date
from typing import Protocol

from .domain import Loan


class LoanStore(Protocol):
    def all(self) -> list[Loan]: ...

    def find(self, loan_id: str) -> Loan | None: ...

    def add(self, loan: Loan) -> Loan: ...

    def save_returned(self, loan: Loan) -> Loan: ...
