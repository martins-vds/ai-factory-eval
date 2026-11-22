from dataclasses import dataclass
from datetime import date

from src.reports.services import MonthlyReportApplication


@dataclass
class Loan:
    id: str
    member: str
    lent_on: date
    due_on: date
    returned_on: date | None = None


@dataclass
class Fee:
    amount_cents: int


class LoanRepository:
    def __init__(self, loans):
        self.loans = loans

    def started_between(self, start, end):
        return [loan for loan in self.loans if start <= loan.lent_on < end]


class FeeCalculator:
    def __init__(self, fees):
        self.fees = fees

    def fee_for(self, loan_id):
        return self.fees[loan_id]


class Clock:
    def today(self):
        return date(2026, 3, 1)


def test_monthly_report_aggregates_previous_calendar_month_loans():
    application = MonthlyReportApplication(
        LoanRepository(
            [
                Loan('L0', 'member-1', date(2026, 1, 31), date(2026, 2, 14)),
                Loan('L1', 'member-1', date(2026, 2, 1), date(2026, 2, 10), date(2026, 2, 13)),
                Loan('L2', 'member-1', date(2026, 2, 28), date(2026, 3, 14)),
                Loan('L3', 'member-2', date(2026, 3, 1), date(2026, 3, 15)),
            ]
        ),
        FeeCalculator({'L1': Fee(75), 'L2': Fee(0)}),
        Clock(),
    )

    rows = application.generate()

    assert [
        (row.member_id, row.loans_started, row.late_returns, row.late_fees_cents)
        for row in rows
    ] == [('member-1', 2, 1, 75)]
