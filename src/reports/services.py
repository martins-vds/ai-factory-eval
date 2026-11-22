from dataclasses import dataclass
from datetime import date
from typing import Iterable, Protocol


class LoanRecord(Protocol):
    member: str
    lent_on: date
    due_on: date
    returned_on: date | None


class LoanRepository(Protocol):
    def for_period(self, start: date, end: date) -> Iterable[LoanRecord]: ...


class Clock(Protocol):
    def today(self) -> date: ...


@dataclass(frozen=True)
class MonthlyReportRow:
    member_id: str
    loans_started: int
    late_returns: int
    late_fees_cents: int


class MonthlyReportApplication:
    def __init__(self, repository: LoanRepository, clock: Clock):
        self.repository = repository
        self.clock = clock

    def generate(self) -> list[MonthlyReportRow]:
        today = self.clock.today()
        period_end = date(today.year, today.month, 1)
        if today.month == 1:
            period_start = date(today.year - 1, 12, 1)
        else:
            period_start = date(today.year, today.month - 1, 1)

        members = {}
        for loan in self.repository.for_period(period_start, period_end):
            report = members.setdefault(loan.member, [0, 0, 0])
            if period_start <= loan.lent_on < period_end:
                report[0] += 1
            if (
                loan.returned_on is not None
                and period_start <= loan.returned_on < period_end
                and loan.returned_on > loan.due_on
            ):
                report[1] += 1
                days_late = (loan.returned_on - loan.due_on).days
                report[2] += 0 if days_late <= 2 else min(1000, days_late * 25)

        rows = [
            MonthlyReportRow(member, loans_started, late_returns, late_fees_cents)
            for member, (loans_started, late_returns, late_fees_cents) in members.items()
        ]
        return sorted(rows, key=lambda row: (-row.late_fees_cents, row.member_id))
