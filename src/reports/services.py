from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Protocol


class ReportLoan(Protocol):
    id: str
    member: str
    due_on: date
    returned_on: date | None


class LoanRepository(Protocol):
    def started_between(self, start: date, end: date) -> Iterable[ReportLoan]: ...

    def returned_between(self, start: date, end: date) -> Iterable[ReportLoan]: ...


class Clock(Protocol):
    def today(self) -> date: ...


class Fee(Protocol):
    amount_cents: int


class FeeCalculator(Protocol):
    def fee_for(self, loan_id: str) -> Fee | None: ...


@dataclass(frozen=True)
class MemberMonthlyReport:
    member_id: str
    loans_started: int
    late_returns: int
    late_fees_cents: int


@dataclass
class _MemberMetrics:
    loans_started: int = 0
    late_returns: int = 0
    late_fees_cents: int = 0


class MonthlyReportApplication:
    def __init__(self, loans: LoanRepository, clock: Clock, fees: FeeCalculator):
        self.loans = loans
        self.clock = clock
        self.fees = fees

    def generate(self) -> list[MemberMonthlyReport]:
        start, end = previous_month_window(self.clock.today())
        metrics: dict[str, _MemberMetrics] = {}

        for loan in self.loans.started_between(start, end):
            member_metrics = metrics.setdefault(loan.member, _MemberMetrics())
            member_metrics.loans_started += 1

        for loan in self.loans.returned_between(start, end):
            member_metrics = metrics.get(loan.member)
            if (
                member_metrics is None
                or loan.returned_on is None
                or loan.returned_on <= loan.due_on
            ):
                continue

            member_metrics.late_returns += 1
            fee = self.fees.fee_for(loan.id)
            if fee is not None:
                member_metrics.late_fees_cents += fee.amount_cents

        reports = [
            MemberMonthlyReport(
                member_id=member_id,
                loans_started=member_metrics.loans_started,
                late_returns=member_metrics.late_returns,
                late_fees_cents=member_metrics.late_fees_cents,
            )
            for member_id, member_metrics in metrics.items()
        ]
        return sorted(reports, key=lambda report: (-report.late_fees_cents, report.member_id))


def previous_month_window(today: date) -> tuple[date, date]:
    end = today.replace(day=1)
    start = (end - timedelta(days=1)).replace(day=1)
    return start, end
