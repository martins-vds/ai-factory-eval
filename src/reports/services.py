from dataclasses import dataclass
from datetime import date


@dataclass
class _MemberSummary:
    loans_started: int = 0
    loans_returned_late: int = 0
    late_fees_cents: int = 0


@dataclass(frozen=True)
class MonthlyReportRow:
    member_id: str
    loans_started: int
    loans_returned_late: int
    late_fees_cents: int


class MonthlyReportApplication:
    def __init__(self, repository):
        self.repository = repository

    def for_month(self, start: date, end: date, as_of: date) -> list[MonthlyReportRow]:
        summaries = {}
        for loan in self.repository.loans_started_between(start, end):
            summary = summaries.setdefault(loan.member, _MemberSummary())
            summary.loans_started += 1

            fee_end = loan.returned_on if loan.returned_on is not None else as_of
            days_late = max(0, (fee_end - loan.due_on).days)
            if loan.returned_on is not None and days_late > 0:
                summary.loans_returned_late += 1
            if days_late > 2:
                summary.late_fees_cents += min(1000, days_late * 25)

        rows = [
            MonthlyReportRow(
                member_id,
                summary.loans_started,
                summary.loans_returned_late,
                summary.late_fees_cents,
            )
            for member_id, summary in summaries.items()
        ]
        return sorted(rows, key=lambda row: (-row.late_fees_cents, row.member_id))
