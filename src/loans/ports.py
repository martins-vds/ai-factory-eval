from collections.abc import Iterable
from datetime import date
from typing import Protocol


class LoanRecord(Protocol):
    id: str
    member: str
    isbn: str
    lent_on: date
    returned_on: date | None
    due_on: date


class LoanRepositoryPort(Protocol):
    def all(self) -> Iterable[LoanRecord]: ...

    def find(self, loan_id: str) -> LoanRecord | None: ...

    def lend(self, member: str, isbn: str, lent_on: date) -> LoanRecord: ...

    def mark_returned(self, loan_id: str, returned_on: date) -> bool: ...


class Clock(Protocol):
    def today(self) -> date: ...
