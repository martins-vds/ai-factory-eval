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

    def create(self, **fields: object) -> LoanRecord: ...

    def record_return(self, loan_id: str, today: date) -> LoanRecord | None: ...
