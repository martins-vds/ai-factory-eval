from dataclasses import dataclass
from datetime import date, timedelta


class LoanInputError(Exception):
    def __init__(self, fields):
        self.fields = fields


class LoanNotFound(Exception):
    pass


class LoanAlreadyReturned(Exception):
    pass


@dataclass
class Loan:
    id: str
    member: str
    isbn: str
    lent_on: date
    returned_on: date | None = None

    @property
    def due_on(self):
        return self.lent_on + timedelta(days=14)

    def mark_returned(self, returned_on):
        if self.returned_on is not None:
            raise LoanAlreadyReturned
        self.returned_on = returned_on
