from dataclasses import dataclass
from datetime import date

from src.reports.services import MonthlyReportApplication, MonthlyReportRow


@dataclass
class Loan:
    member: str
    lent_on: date
    due_on: date
    returned_on: date | None


class ReportLoanRepository:
    def __init__(self, loans):
        self.loans = loans
        self.period = None

    def for_period(self, start, end):
        self.period = (start, end)
        return self.loans


class Clock:
    def today(self):
        return date(2026, 1, 1)


def test_monthly_report_uses_previous_calendar_month_across_year_boundary():
    repository = ReportLoanRepository(
        [
            Loan('Alpha', date(2025, 12, 1), date(2025, 12, 15), date(2025, 12, 18)),
            Loan('Beta', date(2025, 11, 1), date(2025, 11, 15), date(2025, 12, 20)),
            Loan('Gamma', date(2025, 11, 1), date(2025, 11, 15), date(2025, 12, 20)),
            Loan('First day', date(2025, 11, 1), date(2025, 11, 15), date(2025, 12, 1)),
            Loan('Due date', date(2025, 11, 17), date(2025, 12, 1), date(2025, 12, 1)),
            Loan('On time', date(2025, 12, 31), date(2026, 1, 14), date(2025, 12, 31)),
            Loan('Outside', date(2026, 1, 1), date(2026, 1, 15), None),
            Loan('End boundary', date(2025, 11, 1), date(2025, 11, 15), date(2026, 1, 1)),
        ]
    )

    report = MonthlyReportApplication(repository, Clock()).generate()

    assert repository.period == (date(2025, 12, 1), date(2026, 1, 1))
    assert report == [
        MonthlyReportRow('Beta', 0, 1, 875),
        MonthlyReportRow('Gamma', 0, 1, 875),
        MonthlyReportRow('First day', 0, 1, 400),
        MonthlyReportRow('Alpha', 1, 1, 75),
        MonthlyReportRow('Due date', 0, 0, 0),
        MonthlyReportRow('On time', 1, 0, 0),
    ]
