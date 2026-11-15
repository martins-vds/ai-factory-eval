from collections import defaultdict
from dataclasses import dataclass
from datetime import date

from src.loans.models import Loan


@dataclass(frozen=True)
class MemberMonthlyReport:
    member_id: str
    loans_started: int
    late_returns: int
    late_fees_cents: int


def previous_month_window(today: date) -> tuple[date, date]:
    month_end = today.replace(day=1)
    if month_end.month == 1:
        month_start = date(month_end.year - 1, 12, 1)
    else:
        month_start = date(month_end.year, month_end.month - 1, 1)
    return month_start, month_end


def monthly_report(month_start: date, month_end: date, as_of: date) -> list[MemberMonthlyReport]:
    totals = defaultdict(lambda: [0, 0, 0])
    loans = Loan.objects.filter(lent_on__gte=month_start, lent_on__lt=month_end)

    for loan in loans:
        due_on = loan.due_on
        end_date = loan.returned_on if loan.returned_on is not None else as_of
        days_late = max(0, (end_date - due_on).days)
        total = totals[loan.member]
        total[0] += 1
        total[1] += loan.returned_on is not None and loan.returned_on > due_on
        total[2] += 0 if days_late <= 2 else min(1000, days_late * 25)

    return sorted(
        (MemberMonthlyReport(member_id, *values) for member_id, values in totals.items()),
        key=lambda report: (-report.late_fees_cents, report.member_id),
    )
