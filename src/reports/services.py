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
    def for_period(self, start_on: date, end_on: date) -> Iterable[LoanRecord]: ...


class Clock(Protocol):
    def today(self) -> date: ...


@dataclass(frozen=True)
class MonthlyReportRow:
    member_id: str
    loans_started: int
    late_returns: int
    late_fees_cents: int


class MonthlyReportApplication:
    def __init__(self, loans: LoanRepository, clock: Clock):
        self.loans = loans
        self.clock = clock

    def generate_previous_month_report(self) -> list[MonthlyReportRow]:
        today = self.clock.today()
        end_on = date(today.year, today.month, 1)
        if end_on.month == 1:
            start_on = date(end_on.year - 1, 12, 1)
        else:
            start_on = date(end_on.year, end_on.month - 1, 1)

        totals = {}
        for loan in self.loans.for_period(start_on, end_on):
            member_totals = totals.setdefault(loan.member, [0, 0, 0])
            if start_on <= loan.lent_on < end_on:
                member_totals[0] += 1

            if loan.returned_on is None or not start_on <= loan.returned_on < end_on:
                continue

            days_late = (loan.returned_on - loan.due_on).days
            if days_late > 0:
                member_totals[1] += 1
                if days_late > 2:
                    member_totals[2] += min(1000, days_late * 25)

        rows = [
            MonthlyReportRow(member, *member_totals)
            for member, member_totals in totals.items()
            if member_totals[0] > 0
        ]
        return sorted(rows, key=lambda row: (-row.late_fees_cents, row.member_id))
