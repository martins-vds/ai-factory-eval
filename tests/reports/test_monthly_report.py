from dataclasses import dataclass
from datetime import date, timedelta

import pytest

from src.reports.services import MonthlyReportApplication


@dataclass
class Loan:
    id: str
    member: str
    lent_on: date
    returned_on: date | None = None

    @property
    def due_on(self):
        return self.lent_on + timedelta(days=14)


class LoanRepository:
    def __init__(self, loans):
        self.loans = loans

    def for_period(self, start, end):
        return self.loans


def test_monthly_report_aggregates_and_orders_members_with_monthly_loans():
    application = MonthlyReportApplication(
        LoanRepository(
            [
                Loan('L1', 'B', date(2026, 10, 5), date(2026, 10, 22)),
                Loan('L2', 'B', date(2026, 10, 10), date(2026, 10, 30)),
                Loan('L3', 'A', date(2026, 10, 1), date(2026, 10, 18)),
                Loan('L4', 'C', date(2026, 10, 3), date(2026, 10, 25)),
                Loan('L5', 'Z', date(2026, 9, 1), date(2026, 10, 25)),
                Loan('L6', 'BEFORE', date(2026, 9, 30)),
                Loan('L7', 'END', date(2026, 11, 1)),
            ]
        )
    )

    report = application.run(date(2026, 10, 1), date(2026, 11, 1))

    assert [
        (row.member_id, row.loans_started, row.late_returns, row.total_late_fees_cents)
        for row in report
    ] == [
        ('B', 2, 2, 225),
        ('C', 1, 1, 200),
        ('A', 1, 1, 75),
    ]


@pytest.mark.parametrize(
    ('days_late', 'expected_late_returns', 'expected_fees'),
    [(0, 0, 0), (1, 1, 0), (2, 1, 0), (3, 1, 75), (40, 1, 1000), (100, 1, 1000)],
)
def test_monthly_report_applies_late_return_grace_period_and_fee_cap(
    days_late, expected_late_returns, expected_fees
):
    due_on = date(2026, 10, 14) - timedelta(days=days_late)
    returned_on = due_on + timedelta(days=days_late)
    application = MonthlyReportApplication(
        LoanRepository(
            [
                Loan('L1', 'member', due_on - timedelta(days=14), returned_on),
                Loan('L2', 'member', date(2026, 10, 2)),
            ]
        )
    )

    report = application.run(date(2026, 10, 1), date(2026, 11, 1))

    assert [
        (row.member_id, row.loans_started, row.late_returns, row.total_late_fees_cents)
        for row in report
    ] == [('member', 1, expected_late_returns, expected_fees)]
