from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta
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


@dataclass(frozen=True)
class MonthlyReportRow:
    member_id: str
    loans_started: int
    late_returns: int
    late_fees_cents: int


@dataclass
class _ReportTotals:
    loans_started: int = 0
    late_returns: int = 0
    late_fees_cents: int = 0


class MonthlyReport:
    def __init__(self, loans: LoanRepository, clock: Clock):
        self.loans = loans
        self.clock = clock

    def generate(self) -> list[MonthlyReportRow]:
        as_of = self.clock.today()
        period_end = as_of.replace(day=1)
        period_start = (period_end - timedelta(days=1)).replace(day=1)
        totals: dict[str, _ReportTotals] = {}

        for loan in self.loans.all():
            if not period_start <= loan.lent_on < period_end:
                continue

            member_totals = totals.setdefault(loan.member, _ReportTotals())
            member_totals.loans_started += 1

            end = loan.returned_on if loan.returned_on is not None else as_of
            days_late = max(0, (end - loan.due_on).days)
            if loan.returned_on is not None and days_late > 0:
                member_totals.late_returns += 1
            if days_late > 2:
                member_totals.late_fees_cents += min(1000, days_late * 25)

        rows = [
            MonthlyReportRow(member_id, **vars(member_totals))
            for member_id, member_totals in totals.items()
        ]
        return sorted(rows, key=lambda row: (-row.late_fees_cents, row.member_id))
