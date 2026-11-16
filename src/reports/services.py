from dataclasses import dataclass
from datetime import date, timedelta

from src.loans.models import Loan


@dataclass(frozen=True)
class MemberMonthlyReport:
    member: str
    loans_started: int
    late_returns: int
    late_fees_cents: int


def monthly_report(period_start: date, period_end: date) -> list[MemberMonthlyReport]:
    members = {}
    period_last_day = period_end - timedelta(days=1)
    loans = Loan.objects.filter(lent_on__gte=period_start, lent_on__lt=period_end)

    for loan in loans:
        report = members.setdefault(loan.member, [0, 0, 0])
        report[0] += 1
        due_on = loan.due_on
        returned_in_period = loan.returned_on is not None and loan.returned_on < period_end
        if returned_in_period and loan.returned_on > due_on:
            report[1] += 1

        fee_end = min(loan.returned_on, period_last_day) if loan.returned_on else period_last_day
        days_late = max(0, (fee_end - due_on).days)
        if days_late > 2:
            report[2] += min(1000, days_late * 25)

    return [
        MemberMonthlyReport(member, *totals)
        for member, totals in sorted(members.items(), key=lambda entry: (-entry[1][2], entry[0]))
    ]
