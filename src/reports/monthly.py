from dataclasses import dataclass
from datetime import date, timedelta

from django.db.models import Q

from src.loans.models import Loan


@dataclass(frozen=True)
class MonthlyReportRow:
    member_id: str
    loans_started: int
    late_returns: int
    late_fees_cents: int


def previous_month_report(as_of: date) -> list[MonthlyReportRow]:
    month_end = as_of.replace(day=1)
    previous_month_end = month_end - timedelta(days=1)
    month_start = previous_month_end.replace(day=1)
    rows = {}

    loans = Loan.objects.filter(
        Q(lent_on__gte=month_start, lent_on__lt=month_end)
        | Q(returned_on__gte=month_start, returned_on__lt=month_end)
    ).only('member', 'lent_on', 'returned_on')

    for loan in loans:
        row = rows.setdefault(loan.member, MonthlyReportRow(loan.member, 0, 0, 0))
        loans_started = row.loans_started
        late_returns = row.late_returns
        late_fees_cents = row.late_fees_cents

        if month_start <= loan.lent_on < month_end:
            loans_started += 1

        if loan.returned_on is not None and month_start <= loan.returned_on < month_end:
            days_late = max(0, (loan.returned_on - loan.due_on).days)
            if days_late > 0:
                late_returns += 1
            if days_late > 2:
                late_fees_cents += min(1000, days_late * 25)

        rows[loan.member] = MonthlyReportRow(
            loan.member,
            loans_started,
            late_returns,
            late_fees_cents,
        )

    return sorted(
        (row for row in rows.values() if row.loans_started),
        key=lambda row: (-row.late_fees_cents, row.member_id),
    )
