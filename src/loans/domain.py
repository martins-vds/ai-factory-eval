from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Loan:
    id: str
    member: str
    isbn: str
    lent_on: date
    returned_on: date | None
