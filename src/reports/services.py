import csv
from dataclasses import dataclass
from datetime import date
from io import StringIO

from django.db.models import Q

from src.loans.models import Loan


@dataclass
class MemberMonthlyReport:
    member: str
    loans_started: int = 0
    late_returns: int = 0
    late_fees_cents: int = 0


def monthly_report(start: date, end: date) -> list[MemberMonthlyReport]:
    members = {}
    loans = Loan.objects.filter(
        Q(lent_on__gte=start, lent_on__lt=end) | Q(returned_on__gte=start, returned_on__lt=end)
    ).only('id', 'member', 'lent_on', 'returned_on')

    for loan in loans:
        report = members.setdefault(loan.member, MemberMonthlyReport(loan.member))
        if start <= loan.lent_on < end:
            report.loans_started += 1
        if loan.returned_on and start <= loan.returned_on < end:
            days_late = (loan.returned_on - loan.due_on).days
            if days_late > 0:
                report.late_returns += 1
                if days_late > 2:
                    report.late_fees_cents += min(1000, days_late * 25)

    return sorted(
        (report for report in members.values() if report.loans_started),
        key=lambda report: (-report.late_fees_cents, report.member),
    )


def render_csv(reports: list[MemberMonthlyReport]) -> str:
    output = StringIO(newline='')
    writer = csv.writer(output, lineterminator='\n')
    writer.writerow(['member_id', 'loans_started', 'late_returns', 'late_fees_cents'])
    writer.writerows(
        (
            report.member,
            report.loans_started,
            report.late_returns,
            report.late_fees_cents,
        )
        for report in reports
    )
    return output.getvalue()
