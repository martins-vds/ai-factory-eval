from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Protocol

LATE_FEE_GRACE_DAYS = 2
LATE_FEE_CENTS_PER_DAY = 25
MAX_LATE_FEE_CENTS = 1000


class LoanRecord(Protocol):
    member: str
    due_on: date
    lent_on: date
    returned_on: date | None


class LoanRepository(Protocol):
    def started_between(self, start: date, end: date) -> Iterable[LoanRecord]: ...


class Clock(Protocol):
    def today(self) -> date: ...


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


class MonthlyReportApplication:
    def __init__(self, loans: LoanRepository, clock: Clock):
        self.loans = loans
        self.clock = clock

    def run(self) -> list[MonthlyReportRow]:
        today = self.clock.today()
        end = today.replace(day=1)
        start = (end - timedelta(days=1)).replace(day=1)
        totals = defaultdict(_MemberTotals)

        for loan in self.loans.started_between(start, end):
            member_totals = totals[loan.member]
            member_totals.loans_started += 1
            fee_date = loan.returned_on or today
            days_late = max(0, (fee_date - loan.due_on).days)
            if loan.returned_on is not None and days_late > 0:
                member_totals.late_returns += 1
            if days_late > LATE_FEE_GRACE_DAYS:
                member_totals.total_late_fees_cents += min(
                    MAX_LATE_FEE_CENTS, days_late * LATE_FEE_CENTS_PER_DAY
                )

        rows = [
            MonthlyReportRow(
                member_id,
                member_totals.loans_started,
                member_totals.late_returns,
                member_totals.total_late_fees_cents,
            )
            for member_id, member_totals in totals.items()
        ]
        return sorted(rows, key=lambda row: (-row.total_late_fees_cents, row.member_id))
