from dataclasses import dataclass
from collections.abc import Iterable
from datetime import date, timedelta
from typing import Protocol


class LoanRecord(Protocol):
    id: str
    member: str
    due_on: date
    lent_on: date
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
    late_fees_cents: int


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

    def generate(self) -> list[MonthlyReportRow]:
        today = self.clock.today()
        month_start = today.replace(day=1)
        previous_month = (month_start - timedelta(days=1)).replace(day=1)

        members = {}
        for loan in self.loans.all():
            if not previous_month <= loan.lent_on < month_start:
                continue

            totals = members.setdefault(loan.member, [0, 0, 0])
            totals[0] += 1
            totals[1] += int(loan.returned_on is not None and loan.returned_on > loan.due_on)
            fee = self.fees.fee_for(loan.id)
            totals[2] += fee.amount_cents if fee else 0

        rows = [
            MonthlyReportRow(member_id, *totals)
            for member_id, totals in members.items()
        ]
        return sorted(rows, key=lambda row: (-row.late_fees_cents, row.member_id))
