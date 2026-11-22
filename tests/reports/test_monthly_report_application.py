from dataclasses import dataclass
from datetime import date, timedelta

from src.reports.services import MonthlyReportApplication, MonthlyReportRow


@dataclass
class Loan:
    id: str
    member: str
    lent_on: date
    returned_on: date | None

    @property
    def due_on(self):
        return self.lent_on + timedelta(days=14)


class LoanRepository:
    def __init__(self, loans):
        self.loans = loans

    def all(self):
        return self.loans


class Fee:
    def __init__(self, amount_cents):
        self.amount_cents = amount_cents


class FeeCalculator:
    def __init__(self, amounts):
        self.amounts = amounts

    def fee_for(self, loan_id):
        return Fee(self.amounts[loan_id])


class Clock:
    def today(self):
        return date(2026, 4, 1)


def test_monthly_report_application_applies_month_rules_and_fee_ordering():
    loans = [
        Loan('Z-start', 'zeta', date(2026, 3, 1), date(2026, 3, 18)),
        Loan('Z-return', 'zeta', date(2026, 2, 1), date(2026, 3, 31)),
        Loan('A-start', 'alpha', date(2026, 3, 2), date(2026, 3, 18)),
        Loan('A-second', 'alpha', date(2026, 3, 4), None),
        Loan('B-start', 'beta', date(2026, 3, 3), date(2026, 3, 18)),
        Loan('B-old', 'beta', date(2026, 1, 1), date(2026, 3, 1)),
        Loan('old-only', 'old-reader', date(2026, 2, 1), date(2026, 3, 18)),
        Loan('end-boundary', 'alpha', date(2026, 2, 15), date(2026, 4, 1)),
    ]
    application = MonthlyReportApplication(
        LoanRepository(loans),
        FeeCalculator(
            {
                'Z-start': 75,
                'Z-return': 825,
                'A-start': 75,
                'B-old': 100,
                'B-start': 75,
                'old-only': 1000,
            }
        ),
        Clock(),
    )

    assert application.generate() == [
        MonthlyReportRow('zeta', 1, 2, 900),
        MonthlyReportRow('beta', 1, 2, 175),
        MonthlyReportRow('alpha', 2, 1, 75),
    ]
