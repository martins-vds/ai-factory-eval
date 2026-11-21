from collections.abc import Iterable
from datetime import date, timedelta
from typing import NamedTuple, Protocol


class LoanRecord(Protocol):
    member: str
    lent_on: date
    due_on: date
    returned_on: date | None


class LoanRepository(Protocol):
    def all(self) -> Iterable[LoanRecord]: ...


class MonthlyReportRow(NamedTuple):
    member: str
    loans_started: int
    late_returns: int
    late_fees_cents: int


class MonthlyReportApplication:
    def __init__(self, repository: LoanRepository):
        self.repository = repository

    def report(self, month_start: date, month_end: date) -> list[MonthlyReportRow]:
        totals: dict[str, list[int]] = {}

        for loan in self.repository.all():
            if not month_start <= loan.lent_on < month_end:
                continue

            member_totals = totals.setdefault(loan.member, [0, 0, 0])
            member_totals[0] += 1

            returned = loan.returned_on
            as_of = month_end - timedelta(days=1)
            if returned is not None and returned <= as_of:
                if returned > loan.due_on:
                    member_totals[1] += 1
                effective_end = returned
            else:
                effective_end = as_of

            days_late = max(0, (effective_end - loan.due_on).days)
            late_fee = 0 if days_late <= 2 else min(1000, days_late * 25)
            member_totals[2] += late_fee

        rows = [
            MonthlyReportRow(member, values[0], values[1], values[2])
            for member, values in totals.items()
        ]
        return sorted(rows, key=lambda row: (-row.late_fees_cents, row.member))
