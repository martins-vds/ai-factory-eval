from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from typing import Protocol


class LoanRecord(Protocol):
    id: str
    member: str
    lent_on: date
    due_on: date
    returned_on: date | None


class LoanFee(Protocol):
    days_late: int
    amount_cents: int


class LoanRepository(Protocol):
    def for_period(self, start_on: date, end_on: date) -> Iterable[LoanRecord]: ...


class FeeCalculator(Protocol):
    def fee_for(self, loan_id: str) -> LoanFee | None: ...


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
    def __init__(self, loans: LoanRepository, clock: Clock, fees: FeeCalculator):
        self.loans = loans
        self.clock = clock
        self.fees = fees

    def generate_previous_month_report(self) -> list[MonthlyReportRow]:
        today = self.clock.today()
        end_on = date(today.year, today.month, 1)
        if end_on.month == 1:
            start_on = date(end_on.year - 1, 12, 1)
        else:
            start_on = date(end_on.year, end_on.month - 1, 1)

        totals: dict[str, _MemberTotals] = {}
        for loan in self.loans.for_period(start_on, end_on):
            member_totals = totals.setdefault(loan.member, _MemberTotals())
            if start_on <= loan.lent_on < end_on:
                member_totals.loans_started += 1

            if loan.returned_on is None or not start_on <= loan.returned_on < end_on:
                continue

            fee = self.fees.fee_for(loan.id)
            if fee is not None and fee.days_late > 0:
                member_totals.late_returns += 1
                member_totals.late_fees_cents += fee.amount_cents

        rows = [
            MonthlyReportRow(
                member,
                member_totals.loans_started,
                member_totals.late_returns,
                member_totals.late_fees_cents,
            )
            for member, member_totals in totals.items()
            if member_totals.loans_started > 0
        ]
        return sorted(rows, key=lambda row: (-row.late_fees_cents, row.member_id))
