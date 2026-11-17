import csv
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from typing import TextIO

from django.db.models import Q
from django.utils import timezone

from src.loans.models import Loan


@dataclass(frozen=True)
class MonthlyReportRow:
    member_id: str
    loans_started: int
    late_returns: int
    late_fees_cents: int


@dataclass
class _MemberTotals:
    loans_started: int = 0
    late_returns: int = 0
    late_fees_cents: int = 0


def monthly_report_rows() -> list[MonthlyReportRow]:
    month_end = timezone.localdate().replace(day=1)
    month_start = (month_end - timedelta(days=1)).replace(day=1)
    totals = defaultdict(_MemberTotals)

    loans = Loan.objects.filter(
        Q(lent_on__gte=month_start, lent_on__lt=month_end)
        | Q(returned_on__gte=month_start, returned_on__lt=month_end)
    ).only('member', 'lent_on', 'returned_on')
    for loan in loans:
        member_totals = totals[loan.member]
        if month_start <= loan.lent_on < month_end:
            member_totals.loans_started += 1

        if loan.returned_on is None or not month_start <= loan.returned_on < month_end:
            continue

        days_late = max(0, (loan.returned_on - loan.due_on).days)
        if days_late:
            member_totals.late_returns += 1
            if days_late > 2:
                member_totals.late_fees_cents += min(1000, days_late * 25)

    rows = [
        MonthlyReportRow(member_id, member.loans_started, member.late_returns, member.late_fees_cents)
        for member_id, member in totals.items()
        if member.loans_started
    ]
    return sorted(rows, key=lambda row: (-row.late_fees_cents, row.member_id))


def write_monthly_report(rows: list[MonthlyReportRow], output: TextIO) -> None:
    writer = csv.writer(output, lineterminator='\n')
    writer.writerow(['member_id', 'loans_started', 'late_returns', 'late_fees_cents'])
    writer.writerows(
        (row.member_id, row.loans_started, row.late_returns, row.late_fees_cents) for row in rows
    )
