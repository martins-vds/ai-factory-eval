from dataclasses import dataclass
from datetime import date, timedelta

from src.loans.models import Loan


@dataclass(frozen=True)
class MemberMonthlyReport:
    member: str
    loans_started: int
    late_returns: int
    late_fees_cents: int


@dataclass
class _MemberTotals:
    loans_started: int = 0
    late_returns: int = 0
    late_fees_cents: int = 0


def monthly_report(period_start: date, period_end: date) -> list[MemberMonthlyReport]:
    members: dict[str, _MemberTotals] = {}
    period_last_day = period_end - timedelta(days=1)
    loans = Loan.objects.filter(lent_on__gte=period_start, lent_on__lt=period_end)

    for loan in loans:
        totals = members.setdefault(loan.member, _MemberTotals())
        totals.loans_started += 1
        due_on = loan.due_on
        returned_in_period = loan.returned_on is not None and loan.returned_on < period_end
        if returned_in_period and loan.returned_on > due_on:
            totals.late_returns += 1

        fee_end = min(loan.returned_on, period_last_day) if loan.returned_on else period_last_day
        days_late = max(0, (fee_end - due_on).days)
        if days_late > 2:
            totals.late_fees_cents += min(1000, days_late * 25)

    return [
        MemberMonthlyReport(
            member,
            totals.loans_started,
            totals.late_returns,
            totals.late_fees_cents,
        )
        for member, totals in sorted(
            members.items(), key=lambda entry: (-entry[1].late_fees_cents, entry[0])
        )
    ]
