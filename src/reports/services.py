import csv
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
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


@dataclass
class _MemberMetrics:
    loans_started: int = 0
    late_returns: int = 0
    late_fees_cents: int = 0


class MonthlyReport:
    def __init__(self, loans: LoanRepository, clock: Clock):
        self.loans = loans
        self.clock = clock

    def generate(self) -> str:
        end = self.clock.today().replace(day=1)
        start = (end - timedelta(days=1)).replace(day=1)
        metrics = defaultdict(_MemberMetrics)

        for loan in self.loans.all():
            if start <= loan.lent_on < end:
                metrics[loan.member].loans_started += 1

            if (
                loan.returned_on is not None
                and start <= loan.returned_on < end
                and loan.returned_on > loan.due_on
            ):
                metrics[loan.member].late_returns += 1
                days_late = (loan.returned_on - loan.due_on).days
                if days_late > 2:
                    metrics[loan.member].late_fees_cents += min(1000, days_late * 25)

        rows = sorted(
            (
                (member, values.loans_started, values.late_returns, values.late_fees_cents)
                for member, values in metrics.items()
                if values.loans_started > 0
            ),
            key=lambda row: (-row[3], row[0]),
        )
        output = StringIO(newline='')
        writer = csv.writer(output, delimiter=';', lineterminator='\n')
        writer.writerows(rows)
        return output.getvalue()
