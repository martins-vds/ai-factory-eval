import csv
from dataclasses import dataclass
from datetime import date, timedelta
from io import StringIO


@dataclass
class Loan:
    id: str
    member: str
    isbn: str
    lent_on: date
    returned_on: date | None

    @property
    def due_on(self) -> date:
        return self.lent_on + timedelta(days=14)


class LoanNotFound(Exception):
    pass


def export_loan(loan: Loan) -> str:
    output = StringIO()
    csv.writer(output, delimiter=';', lineterminator='\n').writerow(
        [
            loan.id,
            loan.member,
            loan.isbn,
            loan.lent_on.isoformat(),
            loan.due_on.isoformat(),
            loan.returned_on.isoformat() if loan.returned_on else '',
        ]
    )
    return output.getvalue()
