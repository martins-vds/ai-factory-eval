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


class Clock(Protocol):
    def today(self) -> date: ...


class Fee(Protocol):
    amount_cents: int


class FeeCalculator(Protocol):
    def fee_for(self, loan_id: str) -> Fee | None: ...


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
        loans: LoanRepository,
        clock: Clock,
        fees: FeeCalculator,
    ):
        self.loans = loans
        self.clock = clock
        self.fees = fees

    def generate(self) -> list[MonthlyReportRow]:
        month_end = self.clock.today().replace(day=1)
        month_start = (month_end - timedelta(days=1)).replace(day=1)
        totals: dict[str, _MemberTotals] = {}

        for loan in self.loans.all():
            member_totals = totals.setdefault(loan.member, _MemberTotals())
            if month_start <= loan.lent_on < month_end:
                member_totals.loans_started += 1

            if (
                loan.returned_on is not None
                and month_start <= loan.returned_on < month_end
                and loan.returned_on > loan.due_on
            ):
                member_totals.late_returns += 1
                fee = self.fees.fee_for(loan.id)
                if fee is not None:
                    member_totals.late_fees_cents += fee.amount_cents

        rows = [
            MonthlyReportRow(
                member_id=member_id,
                loans_started=member_totals.loans_started,
                late_returns=member_totals.late_returns,
                late_fees_cents=member_totals.late_fees_cents,
            )
            for member_id, member_totals in totals.items()
            if member_totals.loans_started > 0
        ]
        return sorted(rows, key=lambda row: (-row.late_fees_cents, row.member_id))
