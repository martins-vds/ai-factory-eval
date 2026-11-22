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
    total_late_fees_cents: int


@dataclass
class _MemberTotals:
    loans_started: int = 0
    late_returns: int = 0
    total_late_fees_cents: int = 0


class MonthlyReportApplication:
    def __init__(self, loans: LoanRepository, fees: FeeCalculator, clock: Clock):
        self.loans = loans
        self.fees = fees
        self.clock = clock

    def generate(self) -> list[MonthlyReportRow]:
        month_end = self.clock.today().replace(day=1)
        month_start = (month_end - timedelta(days=1)).replace(day=1)
        loans = list(self.loans.all())
        totals_by_member = {}

        for loan in loans:
            if month_start <= loan.lent_on < month_end:
                totals = totals_by_member.setdefault(loan.member, _MemberTotals())
                totals.loans_started += 1

        for loan in loans:
            totals = totals_by_member.get(loan.member)
            if (
                totals is None
                or loan.returned_on is None
                or not month_start <= loan.returned_on < month_end
            ):
                continue

            if loan.returned_on > loan.due_on:
                totals.late_returns += 1

            fee = self.fees.fee_for(loan.id)
            if fee is not None:
                totals.total_late_fees_cents += fee.amount_cents

        rows = [
            MonthlyReportRow(
                member_id=member,
                loans_started=totals.loans_started,
                late_returns=totals.late_returns,
                total_late_fees_cents=totals.total_late_fees_cents,
            )
            for member, totals in totals_by_member.items()
        ]
        return sorted(rows, key=lambda row: (-row.total_late_fees_cents, row.member_id))
