from dataclasses import dataclass
from datetime import date, timedelta
from typing import Protocol


class MonthlyReportRepository(Protocol):
    def loans_started_between(self, start: date, end: date): ...

    def loans_returned_between(self, start: date, end: date): ...


@dataclass(frozen=True)
class MemberMonthlyReport:
    member_id: str
    loans_started: int
    loans_returned_late: int
    total_late_fees_cents: int


@dataclass
class _MemberSummary:
    loans_started: int = 0
    loans_returned_late: int = 0
    total_late_fees_cents: int = 0


class MonthlyReport:
    def __init__(self, repository: MonthlyReportRepository):
        self.repository = repository

    def for_previous_month(self, today: date) -> list[MemberMonthlyReport]:
        month_end = today.replace(day=1)
        month_start = (month_end - timedelta(days=1)).replace(day=1)
        summaries = {}

        for loan in self.repository.loans_started_between(month_start, month_end):
            summary = summaries.setdefault(loan.member, _MemberSummary())
            summary.loans_started += 1

        for loan in self.repository.loans_returned_between(month_start, month_end):
            summary = summaries.get(loan.member)
            if summary is None or loan.returned_on <= loan.due_on:
                continue

            summary.loans_returned_late += 1
            days_late = (loan.returned_on - loan.due_on).days
            if days_late > 2:
                summary.total_late_fees_cents += min(1000, days_late * 25)

        return [
            MemberMonthlyReport(
                member_id=member_id,
                loans_started=summary.loans_started,
                loans_returned_late=summary.loans_returned_late,
                total_late_fees_cents=summary.total_late_fees_cents,
            )
            for member_id, summary in sorted(
                summaries.items(),
                key=lambda item: (-item[1].total_late_fees_cents, item[0]),
            )
        ]
