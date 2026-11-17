from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Protocol


class LoanRecord(Protocol):
    id: str
    member: str
    due_on: date
    returned_on: date | None


class MonthlyReportRepository(Protocol):
    def started_between(self, start: date, end: date) -> Iterable[LoanRecord]: ...


class Clock(Protocol):
    def today(self) -> date: ...


@dataclass(frozen=True)
class MonthlyReportRow:
    member: str
    loans_started: int
    late_returns: int
    late_fees_cents: int


class MonthlyReportApplication:
    def __init__(self, repository: MonthlyReportRepository, clock: Clock):
        self.repository = repository
        self.clock = clock

    def generate(self) -> list[MonthlyReportRow]:
        today = self.clock.today()
        month_end = today.replace(day=1)
        previous_month_end = month_end - timedelta(days=1)
        month_start = previous_month_end.replace(day=1)
        totals: dict[str, list[int]] = {}

        for loan in self.repository.started_between(month_start, month_end):
            member_totals = totals.setdefault(loan.member, [0, 0, 0])
            member_totals[0] += 1

            fee_end = loan.returned_on if loan.returned_on is not None else today
            days_late = max(0, (fee_end - loan.due_on).days)
            if loan.returned_on is not None and loan.returned_on > loan.due_on:
                member_totals[1] += 1
            if days_late > 2:
                member_totals[2] += min(1000, days_late * 25)

        rows = [
            MonthlyReportRow(member, loans_started, late_returns, late_fees_cents)
            for member, (loans_started, late_returns, late_fees_cents) in totals.items()
        ]
        return sorted(rows, key=lambda row: (-row.late_fees_cents, row.member))
