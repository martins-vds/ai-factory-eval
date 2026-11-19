from dataclasses import dataclass
from datetime import date, timedelta

from src.reports.services import MonthlyReport, MonthlyReportRow


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

    def all(self):
        return self.loans


class Clock:
    def today(self):
        return date(2026, 3, 1)


def test_monthly_report_summarizes_prior_month_loan_activity():
    application = MonthlyReport(
        LoanRepository(
            [
                Loan('L1', 'ada', date(2026, 2, 1), date(2026, 2, 20)),
                Loan('L2', 'ada', date(2026, 2, 10)),
                Loan('L3', 'bea', date(2026, 2, 2), date(2026, 2, 17)),
                Loan('L4', 'cora', date(2026, 2, 3), date(2026, 2, 18)),
                Loan('L5', 'outside', date(2026, 1, 31), date(2026, 2, 25)),
                Loan('L6', 'future', date(2026, 3, 1)),
            ]
        ),
        Clock(),
    )

    rows = application.generate()

    assert rows == [
        MonthlyReportRow('ada', loans_started=2, late_returns=1, late_fees_cents=250),
        MonthlyReportRow('bea', loans_started=1, late_returns=1, late_fees_cents=0),
        MonthlyReportRow('cora', loans_started=1, late_returns=1, late_fees_cents=0),
    ]
