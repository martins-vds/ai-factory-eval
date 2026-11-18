import csv
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta
from io import StringIO
from typing import Protocol


class LoanRecord(Protocol):
    member: str
    due_on: date
    lent_on: date
    returned_on: date | None


class LoanRepository(Protocol):
    def for_month(self, start: date, end: date) -> Iterable[LoanRecord]: ...


class Clock(Protocol):
    def today(self) -> date: ...


@dataclass
class MemberReport:
    member_id: str
    loans_started: int = 0
    late_returns: int = 0
    late_fees_cents: int = 0


class MonthlyReport:
    def __init__(self, loans: LoanRepository, clock: Clock):
        self.loans = loans
        self.clock = clock

    def render(self) -> str:
        start, end = _previous_month(self.clock.today())
        loans = self.loans.for_month(start, end)
        members = {}

        for loan in loans:
            if start <= loan.lent_on < end:
                report = members.setdefault(loan.member, MemberReport(loan.member))
                report.loans_started += 1

        for loan in loans:
            report = members.get(loan.member)
            if report is None or loan.returned_on is None:
                continue
            if start <= loan.returned_on < end:
                days_late = max(0, (loan.returned_on - loan.due_on).days)
                if days_late:
                    report.late_returns += 1
                if days_late > 2:
                    report.late_fees_cents += min(1000, days_late * 25)

        output = StringIO(newline='')
        writer = csv.writer(output, lineterminator='\n')
        writer.writerow(['member_id', 'loans_started', 'late_returns', 'late_fees_cents'])
        for report in sorted(
            members.values(),
            key=lambda row: (-row.late_fees_cents, row.member_id),
        ):
            writer.writerow(
                [
                    report.member_id,
                    report.loans_started,
                    report.late_returns,
                    report.late_fees_cents,
                ]
            )
        return output.getvalue()


def _previous_month(today: date) -> tuple[date, date]:
    end = today.replace(day=1)
    start = (end - timedelta(days=1)).replace(day=1)
    return start, end
