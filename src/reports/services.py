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


class LoanRepository(Protocol):
    def for_period(self, start_on: date, end_before: date) -> Iterable[LoanRecord]: ...


@dataclass(frozen=True)
class MemberMonthlyReport:
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
    def __init__(self, repository: LoanRepository):
        self.repository = repository

    def generate(self, as_of: date) -> list[MemberMonthlyReport]:
        end_before = as_of.replace(day=1)
        start_on = (end_before - timedelta(days=1)).replace(day=1)
        totals = defaultdict(_MemberTotals)

        for loan in self.repository.for_period(start_on, end_before):
            if start_on <= loan.lent_on < end_before:
                totals[loan.member].loans_started += 1

            if (
                loan.returned_on is not None
                and start_on <= loan.returned_on < end_before
                and loan.returned_on > loan.due_on
            ):
                member_totals = totals[loan.member]
                member_totals.late_returns += 1
                days_late = (loan.returned_on - loan.due_on).days
                if days_late > 2:
                    member_totals.late_fees_cents += min(1000, days_late * 25)

        report = [
            MemberMonthlyReport(member, values.loans_started, values.late_returns, values.late_fees_cents)
            for member, values in totals.items()
            if values.loans_started
        ]
        return sorted(report, key=lambda row: (-row.late_fees_cents, row.member_id))
