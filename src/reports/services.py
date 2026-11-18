from dataclasses import dataclass
from datetime import date, timedelta
from typing import Protocol
from collections.abc import Iterable


class LoanRecord(Protocol):
    id: str
    member: str
    due_on: date
    returned_on: date | None


class LoanRepository(Protocol):
    def started_between(self, start: date, end: date) -> Iterable[LoanRecord]: ...

    def returned_between(self, start: date, end: date) -> Iterable[LoanRecord]: ...


class Fee(Protocol):
    amount_cents: int


class FeeCalculator(Protocol):
    def fee_for(self, loan_id: str) -> Fee | None: ...


class Clock(Protocol):
    def today(self) -> date: ...


@dataclass(frozen=True)
class MonthlyReportRow:
    member_id: str
    loans_started: int
    late_returns: int
    late_fees_cents: int


@dataclass
class _MemberSummary:
    loans_started: int = 0
    late_returns: int = 0
    late_fees_cents: int = 0


class MonthlyReportApplication:
    def __init__(self, loans: LoanRepository, clock: Clock, fees: FeeCalculator):
        self.loans = loans
        self.clock = clock
        self.fees = fees

    def rows(self) -> list[MonthlyReportRow]:
        month_end = self.clock.today().replace(day=1)
        month_start = (month_end - timedelta(days=1)).replace(day=1)
        members: dict[str, _MemberSummary] = {}

        for loan in self.loans.started_between(month_start, month_end):
            summary = members.setdefault(loan.member, _MemberSummary())
            summary.loans_started += 1

        for loan in self.loans.returned_between(month_start, month_end):
            summary = members.get(loan.member)
            if summary is None or loan.returned_on <= loan.due_on:
                continue

            summary.late_returns += 1
            fee = self.fees.fee_for(loan.id)
            if fee is not None:
                summary.late_fees_cents += fee.amount_cents

        return [
            MonthlyReportRow(member_id, summary.loans_started, summary.late_returns, summary.late_fees_cents)
            for member_id, summary in sorted(
                members.items(),
                key=lambda item: (-item[1].late_fees_cents, item[0]),
            )
        ]
