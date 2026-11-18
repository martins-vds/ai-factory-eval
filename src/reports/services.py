from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Protocol


class LoanRecord(Protocol):
    id: str
    member: str
    due_on: date
    returned_on: date | None


class LoanRepository(Protocol):
    def started_in_period(self, start: date, end: date) -> Iterable[LoanRecord]: ...


class FeeRecord(Protocol):
    amount_cents: int


class FeeCalculator(Protocol):
    def fee_for(self, loan_id: str) -> FeeRecord | None: ...


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


class MonthlyReportApplication:
    def __init__(self, loans: LoanRepository, fees: FeeCalculator):
        self.loans = loans
        self.fees = fees

    def monthly_report_for(self, today: date) -> list[MonthlyReportRow]:
        month_end = today.replace(day=1)
        month_start = (month_end - timedelta(days=1)).replace(day=1)
        totals_by_member = {}

        for loan in self.loans.started_in_period(month_start, month_end):
            totals = totals_by_member.setdefault(loan.member, _MemberTotals())
            totals.loans_started += 1
            if loan.returned_on is not None and loan.returned_on > loan.due_on:
                totals.late_returns += 1
            fee = self.fees.fee_for(loan.id)
            if fee is not None:
                totals.late_fees_cents += fee.amount_cents

        rows = [
            MonthlyReportRow(
                member_id=member_id,
                loans_started=totals.loans_started,
                late_returns=totals.late_returns,
                late_fees_cents=totals.late_fees_cents,
            )
            for member_id, totals in totals_by_member.items()
        ]
        return sorted(rows, key=lambda row: (-row.late_fees_cents, row.member_id))
