from dataclasses import dataclass
from datetime import date

from src.reports.services import MonthlyReportApplication, ReportRow


@dataclass
class Loan:
    id: str
    member: str
    lent_on: date
    due_on: date
    returned_on: date | None = None


class LoanRepository:
    def __init__(self, loans):
        self.loans = loans

    def all(self):
        return self.loans


class Clock:
    def today(self):
        return date(2026, 3, 1)


def test_monthly_report_aggregates_prior_month_and_sorts_by_fees_then_member():
    application = MonthlyReportApplication(
        LoanRepository(
            [
                Loan('L1', 'ada', date(2026, 2, 2), date(2026, 2, 16), date(2026, 2, 21)),
                Loan('L2', 'ada', date(2026, 1, 3), date(2026, 1, 17), date(2026, 2, 28)),
                Loan('L3', 'bea', date(2026, 2, 4), date(2026, 2, 18), date(2026, 2, 18)),
                Loan('L4', 'zoe', date(2026, 1, 5), date(2026, 1, 19), date(2026, 2, 20)),
                Loan('L5', 'ada', date(2026, 3, 1), date(2026, 3, 15)),
                Loan('L6', 'ada', date(2026, 2, 5), date(2026, 2, 19), date(2026, 3, 1)),
                Loan('L7', 'amy', date(2026, 2, 8), date(2026, 2, 22)),
            ]
        ),
        Clock(),
    )

    report = application.generate()

    assert report == [
        ReportRow('ada', loans_started=2, loans_returned_late=2, total_late_fees_cents=1125),
        ReportRow('amy', loans_started=1, loans_returned_late=0, total_late_fees_cents=0),
        ReportRow('bea', loans_started=1, loans_returned_late=0, total_late_fees_cents=0),
    ]
