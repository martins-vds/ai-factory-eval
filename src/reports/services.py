from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Protocol


class LoanRecord(Protocol):
    member: str
    lent_on: date
    due_on: date
    returned_on: date | None


class MonthlyReportRepository(Protocol):
    def loans_with_activity(self, start: date, end: date) -> Iterable[LoanRecord]: ...


@dataclass(frozen=True)
class MonthlyReportRow:
    member_id: str
    loans_started: int
    late_returns: int
    total_late_fees_cents: int


@dataclass
class _MemberTotals:
    loans_started: int = 0
    late_returns: int = 0
    total_late_fees_cents: int = 0


def previous_month_bounds(today: date) -> tuple[date, date]:
    end = today.replace(day=1)
    start = (end - timedelta(days=1)).replace(day=1)
    return start, end


class MonthlyReportApplication:
    def __init__(self, repository: MonthlyReportRepository):
        self.repository = repository

    def for_previous_month(self, today: date) -> list[MonthlyReportRow]:
        start, end = previous_month_bounds(today)
        totals_by_member = defaultdict(_MemberTotals)

        for loan in self.repository.loans_with_activity(start, end):
            member_totals = totals_by_member[loan.member]
            if start <= loan.lent_on < end:
                member_totals.loans_started += 1

            if loan.returned_on is None or not start <= loan.returned_on < end:
                continue
            days_late = (loan.returned_on - loan.due_on).days
            if days_late <= 0:
                continue

            member_totals.late_returns += 1
            if days_late > 2:
                member_totals.total_late_fees_cents += min(1000, days_late * 25)

        rows = [
            MonthlyReportRow(
                member_id=member_id,
                loans_started=totals.loans_started,
                late_returns=totals.late_returns,
                total_late_fees_cents=totals.total_late_fees_cents,
            )
            for member_id, totals in totals_by_member.items()
        ]
        return sorted(
            rows,
            key=lambda row: (-row.total_late_fees_cents, row.member_id),
        )
