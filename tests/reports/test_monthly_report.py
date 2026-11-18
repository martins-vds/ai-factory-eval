from dataclasses import dataclass
from datetime import date

from src.reports.services import MemberMonthlyReport, MonthlyReportApplication


@dataclass(frozen=True)
class Loan:
    id: str
    member: str
    lent_on: date
    due_on: date
    returned_on: date | None


class LoanRepository:
    def __init__(self, loans):
        self.loans = loans
        self.requested_period = None

    def for_period(self, start_on, end_before):
        self.requested_period = (start_on, end_before)
        return self.loans


def test_monthly_report_aggregates_previous_month_and_sorts_by_fees_then_member():
    repository = LoanRepository(
        [
            Loan('L1', 'amy', date(2026, 2, 3), date(2026, 2, 10), date(2026, 2, 16)),
            Loan('L2', 'amy', date(2026, 2, 4), date(2026, 2, 10), date(2026, 2, 11)),
            Loan('L3', 'ben', date(2026, 2, 1), date(2026, 2, 2), date(2026, 2, 4)),
            Loan('L4', 'zoe', date(2026, 2, 2), date(2026, 2, 8), date(2026, 2, 8)),
            Loan('L5', 'max', date(2026, 2, 2), date(2025, 11, 7), date(2026, 2, 15)),
            Loan('L6', 'outside', date(2026, 1, 31), date(2026, 2, 2), date(2026, 2, 5)),
            Loan('L7', 'outside', date(2026, 3, 1), date(2026, 3, 15), None),
        ]
    )
    application = MonthlyReportApplication(repository)

    report = application.generate(date(2026, 3, 1))

    assert repository.requested_period == (date(2026, 2, 1), date(2026, 3, 1))
    assert report == [
        MemberMonthlyReport('max', 1, 1, 1000),
        MemberMonthlyReport('amy', 2, 2, 150),
        MemberMonthlyReport('ben', 1, 1, 0),
        MemberMonthlyReport('zoe', 1, 0, 0),
    ]
