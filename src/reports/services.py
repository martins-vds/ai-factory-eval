from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class MonthlyReportRow:
    member_id: str
    loans_started: int
    loans_returned_late: int
    total_late_fees_cents: int


class MonthlyReport:
    def __init__(self, repository):
        self.repository = repository

    def generate(self, starts_on, ends_before):
        totals = defaultdict(
            lambda: {
                'loans_started': 0,
                'loans_returned_late': 0,
                'total_late_fees_cents': 0,
            }
        )

        for loan in self.repository.loans_with_activity_between(starts_on, ends_before):
            if starts_on <= loan.lent_on < ends_before:
                totals[loan.member]['loans_started'] += 1

            if (
                loan.returned_on is not None
                and starts_on <= loan.returned_on < ends_before
                and loan.returned_on > loan.due_on
            ):
                days_late = (loan.returned_on - loan.due_on).days
                fee_cents = 0 if days_late <= 2 else min(1000, days_late * 25)
                totals[loan.member]['loans_returned_late'] += 1
                totals[loan.member]['total_late_fees_cents'] += fee_cents

        rows = [
            MonthlyReportRow(member_id=member_id, **values)
            for member_id, values in totals.items()
            if values['loans_started']
        ]
        return sorted(rows, key=lambda row: (-row.total_late_fees_cents, row.member_id))
