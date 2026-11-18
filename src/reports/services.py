import csv
from collections import defaultdict
from collections.abc import Iterable
from datetime import date, timedelta
from io import StringIO
from typing import Protocol


class LoanRecord(Protocol):
    member: str
    lent_on: date
    due_on: date
    returned_on: date | None


class LoanRepository(Protocol):
    def all(self) -> Iterable[LoanRecord]: ...


class Clock(Protocol):
    def today(self) -> date: ...


class MonthlyReport:
    def __init__(self, loans: LoanRepository, clock: Clock):
        self.loans = loans
        self.clock = clock

    def generate(self) -> str:
        end = self.clock.today().replace(day=1)
        start = (end - timedelta(days=1)).replace(day=1)
        metrics = defaultdict(lambda: [0, 0, 0])

        for loan in self.loans.all():
            if start <= loan.lent_on < end:
                metrics[loan.member][0] += 1

            if loan.returned_on is not None and start <= loan.returned_on < end:
                if loan.returned_on > loan.due_on:
                    metrics[loan.member][1] += 1
                    days_late = (loan.returned_on - loan.due_on).days
                    if days_late > 2:
                        metrics[loan.member][2] += min(1000, days_late * 25)

        rows = sorted(
            (
                (member, *values)
                for member, values in metrics.items()
                if values[0] > 0
            ),
            key=lambda row: (-row[3], row[0]),
        )
        output = StringIO(newline='')
        writer = csv.writer(output, delimiter=';', lineterminator='\n')
        writer.writerows(rows)
        return output.getvalue()
