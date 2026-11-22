from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Protocol


class LoanRecord(Protocol):
    id: str
    member: str
    lent_on: date
    due_on: date
    returned_on: date | None


class LoanRepository(Protocol):
    def all(self) -> Iterable[LoanRecord]: ...


class FeeRecord(Protocol):
    amount_cents: int


class FeeCalculator(Protocol):
    def fee_for(self, loan_id: str) -> FeeRecord | None: ...


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
    def __init__(self, loans: LoanRepository, fees: FeeCalculator, clock: Clock):
        self.loans = loans
        self.fees = fees
        self.clock = clock

    def generate(self) -> list[MonthlyReportRow]:
        month_end = self.clock.today().replace(day=1)
        month_start = (month_end - timedelta(days=1)).replace(day=1)
        totals: dict[str, _MemberTotals] = {}

        for loan in self.loans.all():
            if not month_start <= loan.lent_on < month_end:
                continue

            member_totals = totals.setdefault(loan.member, _MemberTotals())
            member_totals.loans_started += 1
            if loan.returned_on is not None and loan.returned_on > loan.due_on:
                member_totals.late_returns += 1
            fee = self.fees.fee_for(loan.id)
            if fee is not None:
                member_totals.late_fees_cents += fee.amount_cents

        return [
            MonthlyReportRow(
                member_id,
                member_totals.loans_started,
                member_totals.late_returns,
                member_totals.late_fees_cents,
            )
            for member_id, member_totals in sorted(
                totals.items(),
                key=lambda item: (-item[1].late_fees_cents, item[0]),
            )
        ]
