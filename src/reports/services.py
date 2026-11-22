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
        totals = defaultdict(lambda: [0, 0, 0])

        for loan in self.loans.started_between(month_start, month_end):
            member_totals = totals[loan.member]
            member_totals[0] += 1
            if loan.returned_on is not None and loan.returned_on > loan.due_on:
                member_totals[1] += 1
            member_totals[2] += self.fees.fee_for(loan.id).amount_cents

        return [
            MonthlyReportRow(member_id, *values)
            for member_id, values in sorted(totals.items(), key=lambda item: (-item[1][2], item[0]))
        ]
