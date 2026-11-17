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


@dataclass
class _MemberTotals:
    loans_started: int = 0
    late_returns: int = 0
    late_fees_cents: int = 0


class MonthlyReportApplication:
    def __init__(self, repository: MonthlyReportRepository, clock: Clock):
        self.repository = repository
        self.clock = clock

    def generate(self) -> list[MonthlyReportRow]:
        today = self.clock.today()
        month_end = today.replace(day=1)
        previous_month_end = month_end - timedelta(days=1)
        month_start = previous_month_end.replace(day=1)
        totals: dict[str, _MemberTotals] = {}

        for loan in self.repository.started_between(month_start, month_end):
            member_totals = totals.setdefault(loan.member, _MemberTotals())
            member_totals.loans_started += 1

            fee_end = loan.returned_on if loan.returned_on is not None else today
            days_late = max(0, (fee_end - loan.due_on).days)
            if loan.returned_on is not None and loan.returned_on > loan.due_on:
                member_totals.late_returns += 1
            if days_late > 2:
                member_totals.late_fees_cents += min(1000, days_late * 25)

        rows = [
            MonthlyReportRow(
                member,
                totals.loans_started,
                totals.late_returns,
                totals.late_fees_cents,
            )
            for member, totals in totals.items()
        ]
        return sorted(rows, key=lambda row: (-row.late_fees_cents, row.member))
