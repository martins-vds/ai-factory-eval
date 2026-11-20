from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Protocol


class LoanRecord(Protocol):
    member: str
    due_on: date
    lent_on: date
    returned_on: date | None


class LoanRepository(Protocol):
    def for_period(self, start: date, end: date) -> Iterable[LoanRecord]: ...


@dataclass(frozen=True)
class MemberReport:
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
    def __init__(self, loans: LoanRepository):
        self.loans = loans

    def run_previous_month(self, today: date) -> list[MemberReport]:
        end = today.replace(day=1)
        start = (end - timedelta(days=1)).replace(day=1)
        return self.run(start, end)

    def run(self, start: date, end: date) -> list[MemberReport]:
        totals: dict[str, _MemberTotals] = {}
        for loan in self.loans.for_period(start, end):
            started_this_month = start <= loan.lent_on < end
            returned_this_month = (
                loan.returned_on is not None and start <= loan.returned_on < end
            )
            if not started_this_month and not returned_this_month:
                continue

            totals.setdefault(loan.member, _MemberTotals())
            if started_this_month:
                totals[loan.member].loans_started += 1

            if returned_this_month:
                days_late = max(0, (loan.returned_on - loan.due_on).days)
                if days_late:
                    totals[loan.member].late_returns += 1
                if days_late > 2:
                    totals[loan.member].total_late_fees_cents += min(
                        1000, days_late * 25
                    )

        return sorted(
            (
                MemberReport(
                    member,
                    member_totals.loans_started,
                    member_totals.late_returns,
                    member_totals.total_late_fees_cents,
                )
                for member, member_totals in totals.items()
                if member_totals.loans_started
            ),
            key=lambda row: (-row.total_late_fees_cents, row.member_id),
        )
