from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from typing import Protocol


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


@dataclass
class _MemberTotals:
    loans_started: int = 0
    late_returns: int = 0
    late_fees_cents: int = 0


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

        members: dict[str, _MemberTotals] = {}
        for loan in self.repository.for_period(period_start, period_end):
            started_this_month = period_start <= loan.lent_on < period_end
            returned_this_month = (
                loan.returned_on is not None and period_start <= loan.returned_on < period_end
            )
            if not started_this_month and not returned_this_month:
                continue

            report = members.setdefault(loan.member, _MemberTotals())
            if started_this_month:
                report.loans_started += 1
            if returned_this_month and loan.returned_on > loan.due_on:
                report.late_returns += 1
                days_late = (loan.returned_on - loan.due_on).days
                report.late_fees_cents += 0 if days_late <= 2 else min(1000, days_late * 25)

        rows = [
            MonthlyReportRow(
                member, totals.loans_started, totals.late_returns, totals.late_fees_cents
            )
            for member, totals in members.items()
            if totals.loans_started > 0
        ]
        return sorted(rows, key=lambda row: (-row.late_fees_cents, row.member_id))
