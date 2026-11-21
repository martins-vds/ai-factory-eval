from dataclasses import dataclass
from collections.abc import Iterable
from datetime import date, timedelta
from typing import Protocol


class LoanRecord(Protocol):
    member: str
    lent_on: date
    due_on: date
    returned_on: date | None


class LoanRepository(Protocol):
    def started_between(self, start: date, end: date) -> Iterable[LoanRecord]: ...


@dataclass
class MonthlyReportRow:
    member_id: str
    loans_started: int = 0
    late_returns: int = 0
    late_fees_cents: int = 0


class MonthlyReportApplication:
    def __init__(self, loans: LoanRepository):
        self.loans = loans

    def run(self, as_of: date) -> list[MonthlyReportRow]:
        period_end = as_of.replace(day=1)
        period_start = (period_end - timedelta(days=1)).replace(day=1)
        members = {}

        for loan in self.loans.started_between(period_start, period_end):
            member = members.setdefault(loan.member, MonthlyReportRow(loan.member))
            member.loans_started += 1
            member.late_returns += int(
                loan.returned_on is not None and loan.returned_on > loan.due_on
            )

            fee_end = loan.returned_on if loan.returned_on is not None else as_of
            days_late = max(0, (fee_end - loan.due_on).days)
            member.late_fees_cents += 0 if days_late <= 2 else min(1000, days_late * 25)

        return sorted(
            members.values(),
            key=lambda member: (-member.late_fees_cents, member.member_id),
        )
