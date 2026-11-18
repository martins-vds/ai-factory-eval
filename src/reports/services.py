from dataclasses import dataclass
from datetime import date, timedelta
from typing import Protocol


class LoanRecord(Protocol):
    member: str
    due_on: date
    lent_on: date
    returned_on: date | None


class LoanRepository(Protocol):
    def started_between(self, start: date, end: date) -> list[LoanRecord]: ...


class Clock(Protocol):
    def today(self) -> date: ...


@dataclass(frozen=True)
class MonthlyReportRow:
    member_id: str
    loans_started: int
    late_returns: int
    total_late_fees_cents: int


class MonthlyReportApplication:
    def __init__(self, loans: LoanRepository, clock: Clock):
        self.loans = loans
        self.clock = clock

    def run(self) -> list[MonthlyReportRow]:
        today = self.clock.today()
        end = today.replace(day=1)
        start = (end - timedelta(days=1)).replace(day=1)
        totals = {}

        for loan in self.loans.started_between(start, end):
            member_totals = totals.setdefault(loan.member, [0, 0, 0])
            member_totals[0] += 1
            fee_date = loan.returned_on or today
            days_late = max(0, (fee_date - loan.due_on).days)
            if loan.returned_on is not None and days_late > 0:
                member_totals[1] += 1
            if days_late > 2:
                member_totals[2] += min(1000, days_late * 25)

        rows = [
            MonthlyReportRow(member_id, *member_totals)
            for member_id, member_totals in totals.items()
        ]
        return sorted(rows, key=lambda row: (-row.total_late_fees_cents, row.member_id))
