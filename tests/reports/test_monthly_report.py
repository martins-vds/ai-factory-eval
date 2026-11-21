from dataclasses import dataclass
from datetime import date

from src.reports.services import MonthlyReportApplication


@dataclass
class Loan:
    member: str
    lent_on: date
    due_on: date
    returned_on: date | None = None


class LoanRepository:
    def __init__(self, loans):
        self.loans = loans
        self.period = None

    def started_between(self, start, end):
        self.period = (start, end)
        return [
            loan for loan in self.loans if start <= loan.lent_on < end
        ]


def test_monthly_report_aggregates_prior_month_and_orders_members():
    repository = LoanRepository(
        [
            Loan('member-b', date(2026, 2, 1), date(2026, 2, 15), date(2026, 2, 18)),
            Loan('member-a', date(2026, 2, 2), date(2026, 2, 16), date(2026, 2, 18)),
            Loan('member-c', date(2026, 2, 3), date(2026, 2, 17)),
            Loan('outside-month', date(2026, 1, 31), date(2026, 2, 14), date(2026, 2, 17)),
            Loan('next-month', date(2026, 3, 1), date(2026, 3, 15)),
        ]
    )

    report = MonthlyReportApplication(repository).run(date(2026, 3, 1))

    assert repository.period == (date(2026, 2, 1), date(2026, 3, 1))
    assert report == [
        {
            'member_id': 'member-c',
            'loans_started': 1,
            'late_returns': 0,
            'late_fees_cents': 350,
        },
        {
            'member_id': 'member-b',
            'loans_started': 1,
            'late_returns': 1,
            'late_fees_cents': 75,
        },
        {
            'member_id': 'member-a',
            'loans_started': 1,
            'late_returns': 1,
            'late_fees_cents': 0,
        },
    ]
