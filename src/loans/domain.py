from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class Loan:
    id: str
    member: str
    isbn: str
    lent_on: date
    returned_on: date | None

    @property
    def due_on(self) -> date:
        return self.lent_on + timedelta(days=14)
