from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Protocol


class ReportLoan(Protocol):
    id: str
    member: str
    returned_on: date | None


class LoanRepository(Protocol):
    def started_between(self, start: date, end: date) -> Iterable[ReportLoan]: ...


class Fee(Protocol):
    days_late: int
    amount_cents: int


class FeeCalculator(Protocol):
    def fee_for(self, loan_id: str) -> Fee | None: ...


class Clock(Protocol):
    def today(self) -> date: ...


@dataclass(frozen=True)
class MemberReport:
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
        loans: LoanRepository,
        fees: FeeCalculator,
        clock: Clock,
    ):
        self.loans = loans
        self.fees = fees
        self.clock = clock

    def generate(self) -> list[MemberReport]:
        today = self.clock.today()
        end = today.replace(day=1)
        start = (end - timedelta(days=1)).replace(day=1)
        totals: dict[str, _MemberTotals] = {}

        for loan in self.loans.started_between(start, end):
            member_totals = totals.setdefault(loan.member, _MemberTotals())
            member_totals.loans_started += 1
            fee = self.fees.fee_for(loan.id)
            if fee is None:
                continue

            if loan.returned_on is not None and fee.days_late > 0:
                member_totals.late_returns += 1
            member_totals.late_fees_cents += fee.amount_cents

        return [
            MemberReport(member, values.loans_started, values.late_returns, values.late_fees_cents)
            for member, values in sorted(
                totals.items(),
                key=lambda item: (-item[1].late_fees_cents, item[0]),
            )
        ]
