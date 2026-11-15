from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class MonthlyReportRow:
    member_id: str
    loans_started: int
    late_returns: int
    late_fees_cents: int


@dataclass
class MonthlyReportTotals:
    loans_started: int = 0
    late_returns: int = 0
    late_fees_cents: int = 0


class MonthlyReportService:
    def __init__(self, repository, fees):
        self.repository = repository
        self.fees = fees

    def for_previous_month(self, today: date) -> list[MonthlyReportRow]:
        end_on = today.replace(day=1)
        start_on = (end_on - timedelta(days=1)).replace(day=1)
        members = {}

        for loan in self.repository.activity_between(start_on, end_on):
            totals = members.setdefault(loan.member, MonthlyReportTotals())
            if start_on <= loan.lent_on < end_on:
                totals.loans_started += 1
            if loan.returned_on and start_on <= loan.returned_on < end_on:
                days_late = max(0, (loan.returned_on - loan.due_on).days)
                if days_late:
                    totals.late_returns += 1
                    fee = self.fees.fee_for(loan.id)
                    if fee is not None:
                        totals.late_fees_cents += fee.amount_cents

        rows = [
            MonthlyReportRow(
                member_id,
                totals.loans_started,
                totals.late_returns,
                totals.late_fees_cents,
            )
            for member_id, totals in members.items()
            if totals.loans_started
        ]
        return sorted(rows, key=lambda row: (-row.late_fees_cents, row.member_id))
