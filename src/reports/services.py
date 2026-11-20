from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Protocol


class LoanRecord(Protocol):
    id: str
    member: str
    due_on: date
    lent_on: date
    returned_on: date | None


class FeeAmount(Protocol):
    amount_cents: int


class LoanRepository(Protocol):
    def for_period(self, start: date, end: date) -> Iterable[LoanRecord]: ...


class FeeCalculator(Protocol):
    def fee_for(self, loan_id: str) -> FeeAmount | None: ...


@dataclass(frozen=True)
class MemberReport:
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
    def __init__(self, loans: LoanRepository, fees: FeeCalculator):
        self.loans = loans
        self.fees = fees

    def run_previous_month(self, today: date) -> list[MemberReport]:
        end = today.replace(day=1)
        start = (end - timedelta(days=1)).replace(day=1)
        return self.run(start, end)

    def run(self, start: date, end: date) -> list[MemberReport]:
        totals: dict[str, _MemberTotals] = {}
        for loan in self.loans.for_period(start, end):
            started_this_month = start <= loan.lent_on < end
            returned_this_month = (
                loan.returned_on is not None and start <= loan.returned_on < end
            )
            if not started_this_month and not returned_this_month:
                continue

            member_totals = totals.setdefault(loan.member, _MemberTotals())
            if started_this_month:
                member_totals.loans_started += 1

            if returned_this_month:
                if loan.returned_on > loan.due_on:
                    member_totals.late_returns += 1
                fee = self.fees.fee_for(loan.id)
                if fee is not None:
                    member_totals.total_late_fees_cents += fee.amount_cents

        return sorted(
            (
                MemberReport(
                    member,
                    member_totals.loans_started,
                    member_totals.late_returns,
                    member_totals.total_late_fees_cents,
                )
                for member, member_totals in totals.items()
                if member_totals.loans_started
            ),
            key=lambda row: (-row.total_late_fees_cents, row.member_id),
        )
