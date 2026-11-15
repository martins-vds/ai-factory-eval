from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta

from src.loans.models import Loan


@dataclass(frozen=True)
class MonthlyReportRow:
    member_id: str
    loans_started: int
    late_returns: int
    late_fees_cents: int


def monthly_report(month_start: date) -> list[MonthlyReportRow]:
    next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
    month_end = next_month - timedelta(days=1)
    summaries = defaultdict(lambda: [0, 0, 0])

    loans = Loan.objects.filter(lent_on__gte=month_start, lent_on__lt=next_month)
    for loan in loans:
        summary = summaries[loan.member]
        summary[0] += 1

        returned_in_month = loan.returned_on is not None and loan.returned_on <= month_end
        if returned_in_month and loan.returned_on > loan.due_on:
            summary[1] += 1

        fee_end = loan.returned_on if returned_in_month else month_end
        days_late = max(0, (fee_end - loan.due_on).days)
        if days_late > 2:
            summary[2] += min(1000, days_late * 25)

    rows = [MonthlyReportRow(member_id, *summary) for member_id, summary in summaries.items()]
    return sorted(rows, key=lambda row: (-row.late_fees_cents, row.member_id))
