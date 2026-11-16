from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta

from django.db.models import Q
from django.utils import timezone

from src.loans.models import Loan


@dataclass(frozen=True)
class MonthlyReportRow:
    member_id: str
    loans_started: int
    late_returns: int
    late_fees_cents: int


def month_bounds(month: str | None = None) -> tuple[date, date]:
    if month is None:
        current_month = timezone.localdate(timezone=timezone.get_default_timezone()).replace(day=1)
        previous_month = current_month - timedelta(days=1)
        start = previous_month.replace(day=1)
    else:
        if len(month) != 7 or month[4] != '-' or not month[:4].isdigit() or not month[5:].isdigit():
            raise ValueError('month must use YYYY-MM format')
        start = date(int(month[:4]), int(month[5:]), 1)
        if start.strftime('%Y-%m') != month:
            raise ValueError('month must use YYYY-MM format')

    if start.month == 12:
        end = date(start.year + 1, 1, 1)
    else:
        end = date(start.year, start.month + 1, 1)
    return start, end


def build_monthly_report(start: date, end: date) -> list[MonthlyReportRow]:
    totals = defaultdict(lambda: [0, 0, 0])
    loans = Loan.objects.filter(
        Q(lent_on__gte=start, lent_on__lt=end) | Q(returned_on__gte=start, returned_on__lt=end)
    ).only('member', 'lent_on', 'returned_on')

    for loan in loans.iterator():
        member_totals = totals[loan.member]
        if start <= loan.lent_on < end:
            member_totals[0] += 1

        if loan.returned_on is not None and start <= loan.returned_on < end:
            days_late = (loan.returned_on - loan.due_on).days
            if days_late > 0:
                member_totals[1] += 1
                if days_late > 2:
                    member_totals[2] += min(1000, days_late * 25)

    rows = [
        MonthlyReportRow(member, *member_totals)
        for member, member_totals in totals.items()
        if member_totals[0] > 0
    ]
    return sorted(rows, key=lambda row: (-row.late_fees_cents, row.member_id))
