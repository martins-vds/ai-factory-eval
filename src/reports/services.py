from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class MonthlyReportRow:
    member_id: str
    loans_started: int
    late_returns: int
    late_fees_cents: int


class MonthlyReportService:
    def __init__(self, repository):
        self.repository = repository

    def for_previous_month(self, today: date) -> list[MonthlyReportRow]:
        end_on = today.replace(day=1)
        start_on = (end_on - timedelta(days=1)).replace(day=1)
        members = {}

        for loan in self.repository.activity_between(start_on, end_on):
            member = members.setdefault(loan.member, [0, 0, 0])
            if start_on <= loan.lent_on < end_on:
                member[0] += 1
            if loan.returned_on and start_on <= loan.returned_on < end_on:
                days_late = max(0, (loan.returned_on - loan.due_on).days)
                if days_late:
                    member[1] += 1
                    if days_late > 2:
                        member[2] += min(1000, days_late * 25)

        rows = [
            MonthlyReportRow(member_id, *totals)
            for member_id, totals in members.items()
            if totals[0]
        ]
        return sorted(rows, key=lambda row: (-row.late_fees_cents, row.member_id))
