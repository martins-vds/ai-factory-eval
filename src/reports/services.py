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


class FeeRecord(Protocol):
    amount_cents: int


class FeeCalculator(Protocol):
    def fee_for(self, loan_id: str) -> FeeRecord | None: ...


@dataclass
class ReportRow:
    member_id: str
    loans_started: int = 0
    loans_returned_late: int = 0
    total_late_fees_cents: int = 0


class MonthlyReportApplication:
    def __init__(self, loans: LoanRepository, clock: Clock, fees: FeeCalculator):
        self.loans = loans
        self.clock = clock
        self.fees = fees

    def generate(self) -> list[ReportRow]:
        loans = list(self.loans.all())
        today = self.clock.today()
        month_end = date(today.year, today.month, 1)
        month_start = (month_end - timedelta(days=1)).replace(day=1)
        rows = {}

        for loan in loans:
            if month_start <= loan.lent_on < month_end:
                row = rows.setdefault(loan.member, ReportRow(loan.member))
                row.loans_started += 1

        for loan in loans:
            if (
                loan.member in rows
                and loan.returned_on is not None
                and month_start <= loan.returned_on < month_end
                and loan.returned_on > loan.due_on
            ):
                row = rows[loan.member]
                row.loans_returned_late += 1
                fee = self.fees.fee_for(loan.id)
                if fee is not None:
                    row.total_late_fees_cents += fee.amount_cents

        return sorted(
            rows.values(),
            key=lambda row: (-row.total_late_fees_cents, row.member_id),
        )
