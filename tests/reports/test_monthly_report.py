from dataclasses import dataclass
from datetime import date

from src.reports.services import MonthlyReport


@dataclass
class Loan:
    id: str
    member: str
    lent_on: date
    due_on: date
    returned_on: date | None


class LoanRepository:
    def __init__(self, loans):
        self.loans = loans

    def all(self):
        return self.loans


class FixedClock:
    def today(self):
        return date(2027, 1, 1)


def test_monthly_report_aggregates_prior_month_activity_and_escapes_csv_fields():
    application = MonthlyReport(
        LoanRepository(
            [
                Loan(
                    'L1',
                    'zee;north',
                    date(2026, 12, 1),
                    date(2026, 12, 15),
                    date(2026, 12, 18),
                ),
                Loan('L2', 'amy', date(2026, 12, 10), date(2026, 12, 24), date(2026, 12, 25)),
                Loan('L3', 'dee', date(2026, 12, 15), date(2026, 12, 29), date(2026, 12, 30)),
                Loan(
                    'L4',
                    'zee;north',
                    date(2026, 11, 15),
                    date(2026, 11, 29),
                    date(2026, 12, 2),
                ),
                Loan('L5', 'mia', date(2026, 11, 15), date(2026, 11, 29), date(2026, 12, 2)),
                Loan('L6', 'dee', date(2026, 11, 15), date(2026, 11, 29), date(2027, 1, 1)),
                Loan('L7', 'amy', date(2027, 1, 1), date(2027, 1, 15), date(2027, 1, 20)),
                Loan('L8', 'zara', date(2026, 12, 1), date(2026, 12, 15), None),
                Loan(
                    'L9',
                    'zara',
                    date(2026, 10, 1),
                    date(2026, 10, 15),
                    date(2026, 12, 31),
                ),
                Loan('L11', 'amy', date(2026, 11, 16), date(2026, 11, 30), date(2026, 12, 1)),
                Loan('L12', 'amy', date(2026, 11, 26), date(2026, 12, 10), date(2026, 12, 10)),
                Loan('L13', 'amy', date(2026, 11, 26), date(2026, 12, 10), date(2026, 12, 12)),
                Loan('L14', 'amy', date(2026, 12, 20), date(2027, 1, 3), None),
            ]
        ),
        FixedClock(),
    )

    report = application.generate()

    assert report == 'zara;1;1;1000\n"zee;north";1;2;150\namy;2;3;0\ndee;1;1;0\n'
