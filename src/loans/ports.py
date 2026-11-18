from datetime import date
from typing import Protocol


class LoanRecord(Protocol):
    id: str
    member: str
    isbn: str
    lent_on: date
    returned_on: date | None
    due_on: date


class LoanStore(Protocol):
    def all(self): ...

    def find(self, loan_id: str) -> LoanRecord | None: ...

    def next_id(self) -> str: ...

    def create(self, **fields) -> LoanRecord: ...

    def return_if_unreturned(self, loan_id: str, returned_on: date) -> bool: ...
