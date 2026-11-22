from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Protocol


class ReportLoan(Protocol):
    id: str
    member: str
    due_on: date
    returned_on: date | None


class ReportLoanRepository(Protocol):
    def started_between(self, start: date, end: date) -> list[ReportLoan]: ...


class FeeCalculator(Protocol):
    def fee_for(self, loan_id: str): ...


class Clock(Protocol):
    def today(self) -> date: ...


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
    def __init__(
        self,
        loans: ReportLoanRepository,
        fees: FeeCalculator,
        clock: Clock,
    ):
        self.loans = loans
        self.fees = fees
        self.clock = clock

    def generate(self) -> list[MonthlyReportRow]:
        month_end = self.clock.today().replace(day=1)
        previous_month_end = month_end - timedelta(days=1)
        month_start = previous_month_end.replace(day=1)
        totals = defaultdict(_MemberTotals)

        for loan in self.loans.started_between(month_start, month_end):
            member_totals = totals[loan.member]
            member_totals.loans_started += 1
            if loan.returned_on is not None and loan.returned_on > loan.due_on:
                member_totals.late_returns += 1
            member_totals.late_fees_cents += self.fees.fee_for(loan.id).amount_cents

        return [
            MonthlyReportRow(
                member_id,
                member_totals.loans_started,
                member_totals.late_returns,
                member_totals.late_fees_cents,
            )
            for member_id, member_totals in sorted(
                totals.items(), key=lambda item: (-item[1].late_fees_cents, item[0])
            )
        ]
