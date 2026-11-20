from dataclasses import dataclass
from datetime import date
from typing import Protocol


class LoanRecord(Protocol):
    member: str
    due_on: date
    lent_on: date
    returned_on: date | None


class LoanRepository(Protocol):
    def for_period(self, start: date, end: date) -> list[LoanRecord]: ...


@dataclass(frozen=True)
class MemberReport:
    member_id: str
    loans_started: int
    late_returns: int
    total_late_fees_cents: int


class MonthlyReportApplication:
    def __init__(self, loans: LoanRepository):
        self.loans = loans

    def run(self, start: date, end: date) -> list[MemberReport]:
        totals = {}
        for loan in self.loans.for_period(start, end):
            started_this_month = start <= loan.lent_on < end
            returned_this_month = (
                loan.returned_on is not None and start <= loan.returned_on < end
            )
            if not started_this_month and not returned_this_month:
                continue

            totals.setdefault(loan.member, [0, 0, 0])
            if started_this_month:
                totals[loan.member][0] += 1

            if returned_this_month:
                days_late = max(0, (loan.returned_on - loan.due_on).days)
                if days_late:
                    totals[loan.member][1] += 1
                if days_late > 2:
                    totals[loan.member][2] += min(1000, days_late * 25)

        return sorted(
            (
                MemberReport(member, *counts)
                for member, counts in totals.items()
                if counts[0]
            ),
            key=lambda row: (-row.total_late_fees_cents, row.member_id),
        )
