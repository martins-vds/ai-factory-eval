from dataclasses import dataclass
from datetime import date, timedelta


def due_date(lent_on: date) -> date:
    return lent_on + timedelta(days=14)


@dataclass(frozen=True)
class Loan:
    id: str
    member: str
    isbn: str
    lent_on: date
    returned_on: date | None

    @property
    def due_on(self) -> date:
        return due_date(self.lent_on)
