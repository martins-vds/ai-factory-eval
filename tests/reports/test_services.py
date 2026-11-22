from dataclasses import dataclass
from datetime import date

from src.reports.services import MonthlyReportApplication, MonthlyReportRow


@dataclass
class Loan:
    member: str
    lent_on: date
    due_on: date
    returned_on: date | None


class LoanRepository:
    def __init__(self, loans):
        self.loans = loans
        self.period = None

    def for_period(self, start, end):
        self.period = (start, end)
        return [
            loan
            for loan in self.loans
            if start <= loan.lent_on < end
            or loan.returned_on is not None
            and start <= loan.returned_on < end
        ]


class Clock:
    def today(self):
        return date(2026, 1, 1)


def test_monthly_report_uses_previous_calendar_month_across_year_boundary():
    repository = LoanRepository(
        [
            Loan('Alpha', date(2025, 12, 1), date(2025, 12, 15), date(2025, 12, 18)),
            Loan('Beta', date(2025, 11, 1), date(2025, 11, 15), date(2025, 12, 20)),
            Loan('Gamma', date(2025, 11, 1), date(2025, 11, 15), date(2025, 12, 20)),
            Loan('On time', date(2025, 12, 31), date(2026, 1, 14), date(2025, 12, 31)),
            Loan('Outside', date(2026, 1, 1), date(2026, 1, 15), None),
        ]
    )

    report = MonthlyReportApplication(repository, Clock()).generate()

    assert repository.period == (date(2025, 12, 1), date(2026, 1, 1))
    assert report == [
        MonthlyReportRow('Beta', 0, 1, 875),
        MonthlyReportRow('Gamma', 0, 1, 875),
        MonthlyReportRow('Alpha', 1, 1, 75),
        MonthlyReportRow('On time', 1, 0, 0),
    ]
